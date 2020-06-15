import ast
import json
import re
import ssl
import time
from datetime import datetime
from threading import Thread

import requests
from bson import ObjectId

from controllers.test_report import save_report_detail, save_report
from controllers.test_suite import get_suite_name
from models.test_case import TestCase
from utils import common
from execution_engine.data_initialize.handler import execute_data_init

ssl._create_default_https_context = ssl._create_unverified_context
requests.packages.urllib3.disable_warnings()

test_conclusion = {
    0: "pass",
    1: "failed",
    2: "error",
    3: "notRun"
}


def get_case_list_by_suite(test_suite_id, include_forbidden=False):
    returned_case_list = []
    sort_query = [('sequence', 1), ('createAt', 1)]
    if test_suite_id:
        if include_forbidden:
            find_query = {
                'testSuiteId': ObjectId(test_suite_id),
                'isDeleted': {'$ne': True}
            }
        else:
            find_query = {
                'testSuiteId': ObjectId(test_suite_id),
                'isDeleted': {'$ne': True},
                'status': True
            }
        for test_case in TestCase.find(find_query).sort(sort_query):
            test_case_dict = common.format_response_in_dic(test_case)
            if 'lastManualResult' in test_case_dict:
                test_case_dict.pop('lastManualResult')
            returned_case_list.append(test_case_dict)
    return returned_case_list


# 异步装饰器
def async_test(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()

    return wrapper


# 基础测试类，负责获取测试用例的参数，请求，验证等信息后，进行测试，测试通过则返回{'status': 'ok'} ，
# 不通过则返回{'status': 'failed'}
class ExecutionEngine:

    def __init__(self, domain, test_env_id=None, global_env_vars=None, test_result_list=None, max_retries=5,
                 global_suite_vars=None):

        # if not test_case_list and not test_suite_list:
        #     raise ValueError('test_case_list and test_suite_list are both None!')
        #
        # if test_case_list and not isinstance(test_case_list, list):
        #     raise TypeError('test_case_list must be a list!')
        #
        # if test_suite_list and not isinstance(test_suite_list, list):
        #     raise TypeError('test_suite_list must be a list!')

        self.test_env_id = test_env_id
        self.domain = domain
        # self.test_case_list = test_case_list
        # self.test_suite_list = test_suite_list
        self.session = requests.Session()

        if isinstance(max_retries, int) and max_retries > 0:
            # 设置连接重试
            adapters = requests.adapters.HTTPAdapter(max_retries=max_retries)
            self.session.mount('https://', adapters)
            self.session.mount('http://', adapters)

        self.test_result_list = test_result_list

        self.global_vars = {}
        if global_env_vars is not None:
            if not isinstance(global_env_vars, dict):
                raise ValueError('global_env_vars must be a dict!')
            self.global_vars.update(global_env_vars)
        if global_suite_vars is not None:
            if not isinstance(global_suite_vars, dict):
                raise ValueError('global_suite_vars must be a dict!')
            self.global_vars.update(global_suite_vars)

    def execute_single_case_test(self, test_case):
        returned_data = dict()
        returned_data["_id"] = ObjectId(test_case["_id"])
        returned_data["testConclusion"] = []
        # 存储 处理过后的testCaseDetail
        returned_data["testCaseDetail"] = {}
        if not isinstance(test_case, dict):
            returned_data["status"] = 'failed'
            returned_data["testConclusion"].append({'resultType': test_conclusion.get(2), 'reason': "测试用例结构不正确"})
            return returned_data

        def validate_test_case(case):
            required_key_list = ['requestProtocol', 'route', 'requestMethod']
            return all([required_key in case for required_key in required_key_list])

        if not validate_test_case(test_case):
            returned_data["status"] = 'failed'
            returned_data["testConclusion"].append({'resultType': test_conclusion.get(2), 'reason': "接口必要参数不完整"})
            return returned_data

        if test_case.get('isClearCookie'):
            self.session.cookies.clear()

        session = self.session

        request_url = None
        request_method = None
        request_headers = dict()
        request_body = None
        check_response_code = None
        check_response_body = None
        check_response_number = None
        set_global_vars = None  # for example {'user': ['data','user']}

        # 获取接口domain
        if 'domain' in test_case and isinstance(test_case["domain"], str) and not test_case["domain"].strip() == '':
            domain = test_case["domain"]
        else:
            domain = self.domain
        # 替换domain中的${service} (如果存在)
        if 'service' in test_case and isinstance(test_case["service"], str) \
                and not test_case["service"].strip() == '':
            domain = common.replace_global_var_for_str(init_var_str=domain,
                                                       global_var_dic={'service': test_case["service"]})

        # 处理url  protocol+domain+route
        route = common.replace_global_var_for_str(init_var_str=test_case['route'], global_var_dic=self.global_vars) \
            if isinstance(test_case['route'], str) else test_case['route']
        request_url = '%s://%s%s' % (test_case['requestProtocol'].lower(), domain, route)
        returned_data['testCaseDetail']['url'] = request_url

        # 获取method
        request_method = test_case['requestMethod']
        returned_data['testCaseDetail']['requestMethod'] = request_method

        # 处理headers
        if 'headers' in test_case and test_case['headers'] not in ["", None, {}, {'': ''}]:
            if isinstance(test_case['headers'], list):
                for header in test_case['headers']:
                    if not header['name'].strip() == '':
                        request_headers[header['name']] = common.replace_global_var_for_str(
                            init_var_str=header['value'],
                            global_var_dic=self.global_vars) \
                            if isinstance(header['value'], str) else header['value']
            else:
                raise TypeError('headers must be list!')
        request_headers = None if request_headers == {} else request_headers
        returned_data['headers'] = request_headers
        # 验证requestBody格式 list[dict]
        if 'requestBody' in test_case and not isinstance(test_case['requestBody'], list):
            raise TypeError("requestBody must be a list")
        if 'requestBody' in test_case and isinstance(test_case['requestBody'], list):
            for list_item in test_case['requestBody']:
                if not isinstance(list_item, dict):
                    raise TypeError("requestBody must be a dict list")

        if 'requestBody' in test_case and len(test_case['requestBody']) > 0:
            if test_case['requestMethod'].lower() == 'get':
                request_url += '?'
                for key, value in test_case['requestBody'][0].items():
                    if value is not None:
                        request_url += '%s=%s&' % (key, value)
                        request_url = common.replace_global_var_for_str(init_var_str=request_url,
                                                                        global_var_dic=self.global_vars)
                request_url = request_url[0:(len(request_url) - 1)]
                returned_data['testCaseDetail']['url'] = request_url
            else:
                # list 先转 str，方便全局变量替换
                test_case['requestBody'] = str(test_case['requestBody'])
                # 全局替换
                request_body_str = common.replace_global_var_for_str(init_var_str=test_case['requestBody'],
                                                                     global_var_dic=self.global_vars)
                # 替换requestBody中的Number类型(去除引号)
                request_body_str = common.replace_global_var_for_str(init_var_str=request_body_str,
                                                                     global_var_dic=self.global_vars,
                                                                     global_var_regex=r'\'\$num{.*?}\'',
                                                                     match2key_sub_string_start_index=6,
                                                                     match2key_sub_string_end_index=-2
                                                                     )
                if 'isJsonArray' not in test_case or not test_case['isJsonArray']:
                    request_body_str = request_body_str[1:-1]
                # 转回 dict or list
                request_body = ast.literal_eval(request_body_str)
                returned_data['testCaseDetail']['requestBody'] = request_body
        # 处理 全局变量
        if 'setGlobalVars' in test_case and test_case['setGlobalVars'] not in [[], {}, "", None]:
            set_global_vars = test_case['setGlobalVars']

        # add by Vincent-Lee for data initial # 2020-1-7 16:40:56
        # 处理数据初始化 dataInitializes
        if 'dataInitializes' in test_case and test_case['dataInitializes'] not in ["", None, {}, {'': ''}]:
            if isinstance(test_case['headers'], list):
                returned_data["dataInitResult"] = []
                for dataInitialize in test_case['dataInitializes']:
                    if not dataInitialize['dbConfigId'].strip() == '':
                        returned_data["dataInitResult"].append(
                            execute_data_init(self.test_env_id, dataInitialize, self.global_vars))

        # 处理 cookies
        test_case['cookies'] = []
        for key, value in session.cookies.items():
            cookie_dic = dict()
            cookie_dic['name'] = key
            cookie_dic['value'] = value
            test_case['cookies'].append(cookie_dic)
        returned_data['testCaseDetail']['cookies'] = test_case['cookies']

        try:
            response = session.request(url=request_url, method=request_method, json=request_body,
                                       headers=request_headers, verify=False)
        except BaseException as e:
            returned_data["status"] = 'failed'
            returned_data["testConclusion"].append(
                {'resultType': test_conclusion.get(1), 'reason': '请求失败, 错误信息: <%s> ' % e})
            return returned_data

        response_status_code = response.status_code
        returned_data["responseStatusCode"] = response_status_code
        returned_data["responseData"] = response.text

        try:
            response_json = json.loads(response.text) if isinstance(response.text,
                                                                    str) and response.text.strip() else {}
        except BaseException as e:
            # 如果出现异常，表明服务器返回格式不是json
            if set_global_vars and isinstance(set_global_vars, list):
                for set_global_var in set_global_vars:
                    if isinstance(set_global_var, dict) and isinstance(set_global_var.get('name'), str):
                        name = set_global_var.get('name')
                        query = set_global_var.get('query')
                        if query and isinstance(query, list):
                            query = common.replace_global_var_for_list(init_var_list=query,
                                                                       global_var_dic=self.global_vars)
                        value = common.dict_get(response.text, query)
                        self.global_vars[name] = str(value) if value else value

            if 'checkResponseCode' in test_case and test_case['checkResponseCode'] not in ["", None]:
                check_response_code = test_case['checkResponseCode']
                returned_data['checkResponseCode'] = check_response_code

            if check_response_code and not str(response_status_code) == str(check_response_code):
                returned_data["status"] = 'failed'
                returned_data["testConclusion"].append(
                    {'resultType': test_conclusion.get(1),
                     'reason': '响应状态码错误, 期待值: <%s>, 实际值: <%s>。\t' % (check_response_code, response_status_code)})
                return returned_data

            is_check_res_body_valid = isinstance(test_case.get('checkResponseBody'), list) and len(
                list(filter(lambda x: str(x.get('regex')).strip() == '', test_case.get('checkResponseBody')))) < 1
            is_check_res_num_valid = isinstance(test_case.get('checkResponseNumber'), list) and len(
                list(filter(lambda x: str(x.get('expressions').get('expectResult')).strip() == '',
                            test_case.get('checkResponseNumber')))) < 1
            is_test_failed = is_check_res_body_valid or is_check_res_num_valid

            returned_data['status'] = 'failed' if is_test_failed else 'ok'
            returned_data["testConclusion"].append(
                {'resultType': test_conclusion.get(1),
                 'reason': '服务器返回格式不是json, 错误信息: %s, 服务器返回为: %s ' % (e, response.text)}) \
                if returned_data.get('status') and returned_data.get('status') == 'failed' else None

            if returned_data['status'] == 'ok':
                returned_data["testConclusion"].append({'resultType': test_conclusion.get(0), 'reason': '测试通过'})
            return returned_data

        if set_global_vars and isinstance(set_global_vars, list):
            for set_global_var in set_global_vars:
                if isinstance(set_global_var, dict) and isinstance(set_global_var.get('name'), str):
                    name = set_global_var.get('name')
                    query = set_global_var.get('query')
                    value = common.dict_get(response_json, query)
                    self.global_vars[name] = str(value) if value else value

        # 校验处理
        # checkResponseCode
        if 'checkResponseCode' in test_case and test_case['checkResponseCode'] not in ["", None]:
            check_response_code = test_case['checkResponseCode']
            returned_data['checkResponseCode'] = check_response_code

        # checkResponseBody
        if 'checkResponseBody' in test_case and test_case['checkResponseBody'] not in [[], {}, "", None]:
            if not isinstance(test_case['checkResponseBody'], list):
                raise TypeError('checkResponseBody must be list！')
            for index, check_item in enumerate(test_case['checkResponseBody']):
                if not isinstance(check_item, dict) or 'regex' not in check_item or 'query' not in check_item or \
                        not isinstance(check_item['regex'], str) or not isinstance(check_item['query'], list):
                    raise TypeError('checkResponseBody is not valid!')
                # TODO 可开启/关闭 全局替换
                # 对校验结果进行全局替换
                test_case['checkResponseBody'][index]['regex'] = common.replace_global_var_for_str(
                    init_var_str=check_item['regex'], global_var_dic=self.global_vars) if check_item.get(
                    'regex') and isinstance(check_item.get('regex'), str) else ''  # 警告！python判断空字符串为False
                if check_item.get('query') and isinstance(check_item.get('query'), list):
                    test_case['checkResponseBody'][index]['query'] = common.replace_global_var_for_list(
                        init_var_list=check_item['query'], global_var_dic=self.global_vars)
            check_response_body = test_case['checkResponseBody']
            returned_data['checkResponseBody'] = check_response_body

        # checkResponseNumber
        if 'checkResponseNumber' in test_case and not test_case['checkResponseNumber'] in [[], {}, "", None]:
            if not isinstance(test_case['checkResponseNumber'], list):
                raise TypeError('checkResponseNumber must be list！')
            for index, check_item in enumerate(test_case['checkResponseNumber']):
                if not isinstance(check_item, dict) or 'expressions' not in check_item or not isinstance(
                        check_item['expressions'], dict):
                    raise TypeError('checkResponseNumber is not valid!')

                test_case['checkResponseNumber'][index]['expressions']['firstArg'] = common.replace_global_var_for_str(
                    init_var_str=check_item['expressions']['firstArg'],
                    global_var_dic=self.global_vars) if check_item['expressions'].get('firstArg') and isinstance(
                    check_item['expressions'].get('firstArg'), str) else ''

                test_case['checkResponseNumber'][index]['expressions']['secondArg'] = common.replace_global_var_for_str(
                    init_var_str=check_item['expressions']['secondArg'],
                    global_var_dic=self.global_vars) if check_item['expressions'].get('secondArg') and isinstance(
                    check_item['expressions'].get('secondArg'), str) else ''

                test_case['checkResponseNumber'][index]['expressions']['expectResult'] = common.replace_global_var_for_str(
                    init_var_str=check_item['expressions']['expectResult'],
                    global_var_dic=self.global_vars) if check_item['expressions'].get('expectResult') and isinstance(
                    check_item['expressions'].get('expectResult'), str) else ''
            check_response_number = test_case['checkResponseNumber']
            returned_data['checkResponseNumber'] = []

        if check_response_code and not str(response_status_code) == str(check_response_code):
            returned_data["status"] = 'failed'
            returned_data["testConclusion"].append(
                {'resultType': test_conclusion.get(1),
                 'reason': '响应状态码错误, 期待值: <%s>, 实际值: <%s>。\t' % (check_response_code, response_status_code)})
        if check_response_body:
            try:
                for check_item in check_response_body:
                    regex = check_item['regex']
                    if regex.strip() == '':
                        continue
                    query = check_item['query']
                    real_value = common.dict_get(response_json, query)
                    if real_value is None:
                        returned_data["status"] = 'failed'
                        returned_data["testConclusion"].append(
                            {'resultType': test_conclusion.get(1),
                             'reason': '未找到正则校验的Json值(查询语句为: %s), 服务器响应为: %s' % (query, response_json)})
                        return returned_data
                    result = re.search(regex, str(real_value))  # python 将regex字符串取了r''(原生字符串)
                    if not result:
                        returned_data["status"] = 'failed'
                        returned_data["testConclusion"].append(
                            {'resultType': test_conclusion.get(1),
                             'reason': '判断响应值错误(查询语句为: %s),响应值应满足正则: <%s>, 实际值: <%s> (%s)。(正则匹配时会将数据转化成string)\t'
                                       % (query, regex, real_value, type(real_value))})
            except BaseException as e:
                returned_data["status"] = 'failed'
                returned_data["testConclusion"].append({'resultType': test_conclusion.get(1),
                                                        'reason': '判断响应值时报错, 错误信息: <%s>。\t' % e})

        if check_response_number:
            try:
                for check_item in check_response_number:
                    expressions = check_item['expressions']
                    if '' in expressions.values() or None in expressions.values():
                        continue
                    expressions_str, result = common.get_numbers_compared_result(expressions)
                    returned_data['checkResponseNumber'].append({'expression': expressions_str})
                    if not result:
                        returned_data["status"] = 'failed'
                        returned_data["testConclusion"].append(
                            {'resultType': test_conclusion.get(1),
                             'reason': '判断数值错误(判断表达式为: %s)。\t' % expressions_str})
            except BaseException as e:
                returned_data["status"] = 'failed'
                returned_data["testConclusion"].append({'resultType': test_conclusion.get(1),
                                                        'reason': '判断数值时报错, 错误信息: <%s>。\t ' % e})
        if not returned_data["testConclusion"]:
            returned_data["status"] = 'ok'
            returned_data["testConclusion"].append({'resultType': test_conclusion.get(0),
                                                    'reason': '测试通过'})
        return returned_data

    def execute_manual_test_by_case(self, test_case_list):
        test_results = []
        for test_case in test_case_list:
            test_start_time = time.time()
            test_start_datetime = datetime.utcnow()
            test_result = self.execute_single_case_test(test_case)
            test_end_time = time.time()
            test_result["testStartTime"] = test_start_datetime
            test_result["spendTimeInSec"] = round(test_end_time - test_start_time, 3)
            test_results.append(test_result)
        return test_results

    def execute_single_suite_test(self, report_id, test_suite_id, include_forbidden=False):
        testing_case_list = get_case_list_by_suite(test_suite_id, include_forbidden=include_forbidden)
        test_suite_result = {
            '_id': ObjectId(test_suite_id),
            'suiteName': get_suite_name(test_suite_id),
            'testStartTime': datetime.utcnow(),
            'totalCount': len(testing_case_list)
        }
        pass_count = 0
        fail_count = 0
        error_count = 0
        suite_start_time = time.time()
        for test_case in testing_case_list:
            test_start_datetime = datetime.utcnow()
            test_start_time = time.time()
            test_result = self.execute_single_case_test(test_case)
            test_end_time = time.time()
            test_result["name"] = test_case['name']
            test_result["testStartTime"] = test_start_datetime
            test_result["spendTimeInSec"] = round(test_end_time - test_start_time, 3)
            save_report_detail(report_id, test_suite_id, test_case['_id'], test_result)
            result_type = test_result['testConclusion'][0]['resultType']
            if result_type == test_conclusion.get(0):
                pass_count += 1
            elif result_type == test_conclusion.get(1):
                fail_count += 1
            elif result_type == test_conclusion.get(2):
                error_count += 1
        suite_end_time = time.time()
        test_suite_result['spendTimeInSec'] = round(suite_end_time - suite_start_time, 3)
        test_suite_result['passCount'] = pass_count
        test_suite_result['failCount'] = fail_count
        test_suite_result['errorCount'] = error_count
        return test_suite_result


# 异步执行，便于调试时及时反馈
@async_test
def execute_test_by_suite_async(report_id, test_report, test_env_id, test_suite_id_list, domain, global_env_vars):
    test_report['testStartTime'] = datetime.utcnow()
    report_total_count = 0
    report_pass_count = 0
    report_fail_count = 0
    report_error_count = 0
    report_start_time = time.time()
    test_report['testSuites'] = {}
    for test_suite_id in test_suite_id_list:
        execute_engine = ExecutionEngine(test_env_id=test_env_id, domain=domain, global_env_vars=global_env_vars)
        test_suite_result = execute_engine.execute_single_suite_test(report_id, test_suite_id)
        test_report['testSuites'][test_suite_id] = test_suite_result
        report_total_count += test_suite_result['totalCount']
        report_pass_count += test_suite_result['passCount']
        report_fail_count += test_suite_result['failCount']
        report_error_count += test_suite_result['errorCount']
    test_report['totalCount'] = report_total_count
    test_report['passCount'] = report_pass_count
    test_report['failCount'] = report_fail_count
    test_report['errorCount'] = report_error_count
    report_end_time = time.time()
    test_report['spendTimeInSec'] = round(report_end_time - report_start_time, 3)
    test_report['createAt'] = datetime.utcnow()
    save_report(test_report)


# 定时任务, 需同步执行
def execute_test_by_suite(report_id, test_report, test_env_id, test_suite_id_list, domain, global_env_vars):
    test_report['testStartTime'] = datetime.utcnow()
    report_total_count = 0
    report_pass_count = 0
    report_fail_count = 0
    report_error_count = 0
    report_start_time = time.time()
    test_report['testSuites'] = {}
    for test_suite_id in test_suite_id_list:
        execute_engine = ExecutionEngine(test_env_id=test_env_id, domain=domain, global_env_vars=global_env_vars)
        test_suite_result = execute_engine.execute_single_suite_test(report_id, test_suite_id)
        test_report['testSuites'][test_suite_id] = test_suite_result
        report_total_count += test_suite_result['totalCount']
        report_pass_count += test_suite_result['passCount']
        report_fail_count += test_suite_result['failCount']
        report_error_count += test_suite_result['errorCount']
    test_report['totalCount'] = report_total_count
    test_report['passCount'] = report_pass_count
    test_report['failCount'] = report_fail_count
    test_report['errorCount'] = report_error_count
    report_end_time = time.time()
    test_report['spendTimeInSec'] = round(report_end_time - report_start_time, 3)
    test_report['createAt'] = datetime.utcnow()
    return test_report


if __name__ == '__main__':
    pass
