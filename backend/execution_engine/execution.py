import ast
import json
import re
import ssl
import time
from datetime import datetime
from multiprocessing import Pool
from threading import Thread

import pytz
import requests
from bson import ObjectId
from flask import current_app
from requests.cookies import RequestsCookieJar

from app import app
from config import Config
from controllers.mail import get_mails_by_group
from controllers.mail_sender import send_cron_email
from controllers.temp_cookies import save_cookies_for_suite, get_cookies_by_suite
from controllers.temp_suite_params import save_temp_params_for_suite, get_temp_params_by_suite
from controllers.test_env_param import get_global_env_vars
from controllers.test_plan_report import save_plan_report
from controllers.test_report import save_report_detail, save_report
from controllers.test_suite import get_suite_name
from execution_engine.data_initialize.handler import execute_data_init
from models.plan import Plan
from models.test_case import TestCase
from models.test_suite import TestSuite
from utils import common
from utils import send_notify
from utils import fake

# useless
ssl._create_default_https_context = ssl._create_unverified_context
requests.packages.urllib3.disable_warnings()

test_conclusion = {
    0: "pass",
    1: "failed",
    2: "error",
    3: "notRun"
}

config = Config()
host_ip = config.get_host()
host_port = config.get_port()


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

    def __init__(self, protocol, domain, test_env_id=None, global_env_vars=None, test_result_list=None, max_retries=5,
                 global_suite_vars=None):
        self.test_env_id = test_env_id
        self.protocol = protocol
        self.domain = domain
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

    def execute_single_case_test(self, test_case, is_debug=False):
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
            required_key_list = ['route', 'requestMethod']
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
        check_spend_seconds = None
        check_response_body = None
        check_response_number = None
        set_global_vars = None  # for example {'user': 'user1'}
        temp_suite_params = dict()
        new_temp_suite_params = dict()

        # 如果是debug测试用例，需要拿到临时Suite变量
        if is_debug:
            if 'testSuiteId' in test_case and test_case["testSuiteId"]:
                temp_suite_params = get_temp_params_by_suite(test_case["testSuiteId"])
                if temp_suite_params:
                    self.global_vars.update(temp_suite_params)

        # 获取接口protocol
        if 'requestProtocol' in test_case and isinstance(test_case["requestProtocol"], str) \
                and (test_case["requestProtocol"] == 'HTTP' or test_case["requestProtocol"] == 'HTTPS'):
            protocol = test_case["requestProtocol"]
        else:
            protocol = self.protocol

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
        request_url = '%s://%s%s' % (protocol.lower(), domain, route)
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
                        request_url = fake.resolve_faker_var(init_faker_var=request_url)
                        request_url = common.replace_global_var_for_str(init_var_str=request_url,
                                                                        global_var_dic=self.global_vars)
                request_url = common.resolve_int_var(init_int_str=request_url)
                request_url = request_url[0:(len(request_url) - 1)]
                returned_data['testCaseDetail']['url'] = request_url
            else:
                # list 先转 str，方便全局变量替换
                test_case['requestBody'] = str(test_case['requestBody'])
                # 替换faker变量
                request_body_str = fake.resolve_faker_var(init_faker_var=test_case['requestBody'])
                # 全局替换
                request_body_str = common.replace_global_var_for_str(init_var_str=request_body_str,
                                                                     global_var_dic=self.global_vars)
                # 替换requestBody中的Number类型(去除引号)
                request_body_str = common.replace_global_var_for_str(init_var_str=request_body_str,
                                                                     global_var_dic=self.global_vars,
                                                                     global_var_regex=r'\'\$num{.*?}\'',
                                                                     match2key_sub_string_start_index=6,
                                                                     match2key_sub_string_end_index=-2
                                                                     )
                # 替换 需要去除引号的 int变量
                request_body_str = common.resolve_int_var(init_int_str=request_body_str)
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

        # 处理 cookies  for 用例组执行
        test_case['cookies'] = []
        for key, value in session.cookies.items():
            cookie_dic = dict()
            cookie_dic['name'] = key
            cookie_dic['value'] = value
            test_case['cookies'].append(cookie_dic)
        returned_data['testCaseDetail']['cookies'] = test_case['cookies']

        # 获取debug时保存的临时 cookies  for 调试用例
        if is_debug and not test_case.get('isClearCookie'):
            request_cookies = get_cookies_by_suite(test_case.get("testSuiteId"))
            returned_data['testCaseDetail']['cookies'] = request_cookies
            if request_cookies:
                cookie_jar = RequestsCookieJar()
                for cookie in request_cookies:
                    cookie_jar.set(cookie['name'], cookie['value'])
                session.cookies.update(cookie_jar)
        try:
            if 'delaySeconds' in test_case and test_case['delaySeconds'] > 0:
                time.sleep(test_case['delaySeconds'])
                returned_data['testCaseDetail']['delaySeconds'] = test_case['delaySeconds']
            else:
                returned_data['testCaseDetail']['delaySeconds'] = 0
            if 'parameterType' in test_case and test_case["parameterType"] == "form":
                response = session.request(url=request_url, method=request_method, data=request_body,
                                           headers=request_headers, verify=False)
            else:
                response = session.request(url=request_url, method=request_method, json=request_body,
                                           headers=request_headers, verify=False)
            returned_data['elapsedSeconds'] = round(response.elapsed.total_seconds(), 3)
            if is_debug:
                # 保存的临时 cookies  for 调试用例
                response_cookies = []
                for key, value in session.cookies.items():
                    cookie_dic = dict()
                    cookie_dic['name'] = key
                    cookie_dic['value'] = value
                    response_cookies.append(cookie_dic)
                if len(response_cookies) > 0:
                    save_cookies_for_suite(test_case.get("testSuiteId"), response_cookies)

        except BaseException as e:
            returned_data["status"] = 'failed'
            returned_data["testConclusion"].append(
                {'resultType': test_conclusion.get(1), 'reason': '请求失败, 错误信息: <%s> ' % e})
            return returned_data

        response_status_code = response.status_code
        returned_data["responseStatusCode"] = response_status_code
        returned_data["responseData"] = response.text

        # checkResponseCode 校验处理
        if 'checkResponseCode' in test_case and test_case['checkResponseCode'] not in ["", None]:
            check_response_code = test_case['checkResponseCode']
            returned_data['checkResponseCode'] = check_response_code

        # checkSpendSeconds 校验处理
        if 'checkSpendSeconds' in test_case and test_case['checkSpendSeconds'] > 0:
            check_spend_seconds = test_case['checkSpendSeconds']
            returned_data['checkSpendSeconds'] = check_spend_seconds

        try:
            response_json = json.loads(response.text) if isinstance(response.text,
                                                                    str) and response.text.strip() else {}
        except BaseException as e:
            # 如果出现异常，表名接口返回格式不是json
            if set_global_vars and isinstance(set_global_vars, list):
                for set_global_var in set_global_vars:
                    if isinstance(set_global_var, dict) and isinstance(set_global_var.get('name'),
                                                                       str) and set_global_var.get('name'):
                        name = set_global_var.get('name')
                        query = set_global_var.get('query')
                        if query and isinstance(query, list):
                            query = common.replace_global_var_for_list(init_var_list=query,
                                                                       global_var_dic=self.global_vars)
                        value = common.dict_get(response.text, query)
                        self.global_vars[name] = str(value) if value else value
                        if is_debug:
                            new_temp_suite_params[name] = str(value) if value else value
            # 保存临时suite 变量
            if is_debug and new_temp_suite_params:
                temp_suite_params.update(new_temp_suite_params)
                save_temp_params_for_suite(test_case.get("testSuiteId"), temp_suite_params)

            if check_response_code and not str(response_status_code) == str(check_response_code):
                returned_data["status"] = 'failed'
                returned_data["testConclusion"].append(
                    {'resultType': test_conclusion.get(1),
                     'reason': '响应状态码错误, 期待值: <%s>, 实际值: <%s>。\t' % (check_response_code, response_status_code)})
                return returned_data

            if check_spend_seconds and check_spend_seconds < returned_data['elapsedSeconds']:
                returned_data["status"] = 'failed'
                returned_data["testConclusion"].append(
                    {'resultType': test_conclusion.get(1),
                     'reason': '请求超时, 期待耗时: %s s, 实际耗时: %s s。\t' % (
                         check_spend_seconds, returned_data['elapsedSeconds'])})
                return returned_data

            # check response number
            need_check_res_num = isinstance(test_case.get('checkResponseNumber'), list) and len(
                list(filter(lambda x: str(x.get('expressions').get('expectResult')).strip() == '',
                            test_case.get('checkResponseNumber')))) < 1
            returned_data['status'] = 'failed' if need_check_res_num else 'ok'
            returned_data["testConclusion"].append(
                {'resultType': test_conclusion.get(1),
                 'reason': '接口返回格式不是json,无法进行数值校验, 错误信息: %s, 接口返回为: %s ' % (e, response.text)}) \
                if returned_data.get('status') and returned_data.get('status') == 'failed' else None

            # checkResponseBody 校验处理
            if 'checkResponseBody' in test_case and test_case['checkResponseBody'] not in [[], {}, "", None]:
                if not isinstance(test_case['checkResponseBody'], list):
                    raise TypeError('checkResponseBody must be list！')
                need_check_response_body = False
                for index, check_item in enumerate(test_case['checkResponseBody']):
                    if not isinstance(check_item, dict) or 'regex' not in check_item or 'query' not in check_item or \
                            not isinstance(check_item['regex'], str) or not isinstance(check_item['query'], list):
                        raise TypeError('checkResponseBody is not valid!')
                    # 对校验结果进行全局替换
                    if len(check_item['regex']) > 0:
                        need_check_response_body = True
                        test_case['checkResponseBody'][index]['regex'] = common.replace_global_var_for_str(
                            init_var_str=check_item['regex'], global_var_dic=self.global_vars) if check_item.get(
                            'regex') and isinstance(check_item.get('regex'), str) else ''  # 警告！python判断空字符串为False
                        if check_item.get('query') and isinstance(check_item.get('query'), list):
                            test_case['checkResponseBody'][index]['query'] = common.replace_global_var_for_list(
                                init_var_list=check_item['query'], global_var_dic=self.global_vars)
                if need_check_response_body:
                    check_response_body = test_case['checkResponseBody']
                    returned_data['checkResponseBody'] = check_response_body

            if check_response_body:
                for check_item in check_response_body:
                    regex = check_item['regex']
                    query = check_item['query']
                    real_value = common.dict_get(response.text, query)
                    if real_value is None:
                        returned_data["status"] = 'failed'
                        returned_data["testConclusion"].append(
                            {'resultType': test_conclusion.get(1),
                             'reason': '未找到匹配的正则校验的值(查询语句为: %s), 服务器响应为: %s' % (query, response.text)})
                        return returned_data
                    result = re.search(regex, str(real_value))  # python 将regex字符串取了r''(原生字符串)
                    if not result:
                        returned_data["status"] = 'failed'
                        returned_data["testConclusion"].append(
                            {'resultType': test_conclusion.get(1),
                             'reason': '判断响应值错误(查询语句为: %s),响应值应满足正则: <%s>, 实际值: <%s> (%s)。(正则匹配时会将数据转化成string)\t'
                                       % (query, regex, real_value, type(real_value))})

            if returned_data['status'] == 'ok':
                returned_data["testConclusion"].append({'resultType': test_conclusion.get(0), 'reason': '测试通过'})
            return returned_data

        if set_global_vars and isinstance(set_global_vars, list):
            for set_global_var in set_global_vars:
                if isinstance(set_global_var, dict) and isinstance(set_global_var.get('name'),
                                                                   str) and set_global_var.get('name'):
                    name = set_global_var.get('name')
                    query = set_global_var.get('query')
                    value = common.dict_get(response_json, query)
                    self.global_vars[name] = str(value) if value else value
                    if is_debug:
                        new_temp_suite_params[name] = str(value) if value else value
        # 保存临时suite 变量
        if is_debug and new_temp_suite_params:
            temp_suite_params.update(new_temp_suite_params)
            save_temp_params_for_suite(test_case.get("testSuiteId"), temp_suite_params)

        # checkResponseBody 校验处理
        if 'checkResponseBody' in test_case and test_case['checkResponseBody'] not in [[], {}, "", None]:
            if not isinstance(test_case['checkResponseBody'], list):
                raise TypeError('checkResponseBody must be list！')
            need_check_response_body = False
            for index, check_item in enumerate(test_case['checkResponseBody']):
                if not isinstance(check_item, dict) or 'regex' not in check_item or 'query' not in check_item or \
                        not isinstance(check_item['regex'], str) or not isinstance(check_item['query'], list):
                    raise TypeError('checkResponseBody is not valid!')
                # 对校验结果进行全局替换
                if len(check_item['regex']) > 0:
                    need_check_response_body = True
                    test_case['checkResponseBody'][index]['regex'] = common.replace_global_var_for_str(
                        init_var_str=check_item['regex'], global_var_dic=self.global_vars) if check_item.get(
                        'regex') and isinstance(check_item.get('regex'), str) else ''  # 警告！python判断空字符串为False
                    if check_item.get('query') and isinstance(check_item.get('query'), list):
                        test_case['checkResponseBody'][index]['query'] = common.replace_global_var_for_list(
                            init_var_list=check_item['query'], global_var_dic=self.global_vars)
            if need_check_response_body:
                check_response_body = test_case['checkResponseBody']
                returned_data['checkResponseBody'] = check_response_body

        # checkResponseNumber 校验处理
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

                test_case['checkResponseNumber'][index]['expressions'][
                    'expectResult'] = common.replace_global_var_for_str(
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

        if check_spend_seconds and check_spend_seconds < returned_data['elapsedSeconds']:
            returned_data["status"] = 'failed'
            returned_data["testConclusion"].append(
                {'resultType': test_conclusion.get(1),
                 'reason': '请求超时, 期待耗时: %s s, 实际耗时: %s s。\t' % (
                     check_spend_seconds, returned_data['elapsedSeconds'])})
            return returned_data

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
            test_result = self.execute_single_case_test(test_case, is_debug=True)
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
def execute_test_by_suite_async(report_id, test_report, test_env_id, test_suite_id_list, protocol, domain,
                                global_env_vars):
    test_report['testStartTime'] = datetime.utcnow()
    report_total_count = 0
    report_pass_count = 0
    report_fail_count = 0
    report_error_count = 0
    report_start_time = time.time()
    test_report['testSuites'] = {}
    for test_suite_id in test_suite_id_list:
        execute_engine = ExecutionEngine(test_env_id=test_env_id, protocol=protocol, domain=domain,
                                         global_env_vars=global_env_vars)
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
def execute_test_by_suite(report_id, test_report, test_env_id, test_suite_id_list, protocol, domain, global_env_vars):
    test_report['testStartTime'] = datetime.utcnow()
    report_total_count = 0
    report_pass_count = 0
    report_fail_count = 0
    report_error_count = 0
    report_start_time = time.time()
    test_report['testSuites'] = {}
    for test_suite_id in test_suite_id_list:
        execute_engine = ExecutionEngine(test_env_id=test_env_id, protocol=protocol, domain=domain,
                                         global_env_vars=global_env_vars)
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


@async_test
def execute_plan_async(plan_id, plan_report_id, test_plan_report, test_env_id, env_name, protocol, domain,
                       execution_mode="planManual"):
    # validate plan id
    res_plan = common.format_response_in_dic(Plan.find_one({'_id': ObjectId(plan_id)}))
    execution_range = list(map(get_project_execution_range, res_plan.get("executionRange")))
    is_parallel = res_plan.get('isParallel')
    plan_name = res_plan.get('name')
    always_send_mail = res_plan.get('alwaysSendMail')
    alarm_mail_group_list = res_plan.get('alarmMailGroupList')

    enable_wxwork_notify = res_plan.get('enableWXWorkNotify')
    wxwork_api_key = res_plan.get('WXWorkAPIKey')
    mentioned_mobile_list = res_plan.get('WXWorkMentionMobileList')
    always_wxwork_notify = res_plan.get('alwaysWXWorkNotify')

    enable_ding_talk_notify = res_plan.get('enableDingTalkNotify')
    ding_talk_access_token = res_plan.get('DingTalkAccessToken')
    ding_talk_at_mobiles = res_plan.get('DingTalkAtMobiles')
    ding_talk_secret = res_plan.get('DingTalkSecret')
    always_ding_talk_notify = res_plan.get('alwaysDingTalkNotify')

    # test plan report
    test_plan_report['testStartTime'] = datetime.utcnow()
    plan_total_count = 0
    plan_pass_count = 0
    plan_fail_count = 0
    plan_error_count = 0
    plan_start_time = time.time()
    try:
        if is_parallel:
            counts = []
            pool = Pool(processes=len(execution_range))
            for item in execution_range:
                count_dict = pool.apply_async(execute_single_project,
                                              (item, plan_report_id, test_env_id, env_name, protocol, domain,
                                               execution_mode))
                counts.append(count_dict)
            pool.close()
            pool.join()
            for count in counts:
                plan_total_count += int(count.get().get("total_count"))
                plan_pass_count += int(count.get().get("pass_count"))
                plan_fail_count += int(count.get().get("fail_count"))
                plan_error_count += int(count.get().get("error_count"))
        else:
            for item in execution_range:
                count_dict = execute_single_project(item, plan_report_id, test_env_id, env_name, protocol, domain,
                                                    execution_mode)
                plan_total_count += count_dict.get("total_count")
                plan_pass_count += count_dict.get("pass_count")
                plan_fail_count += count_dict.get("fail_count")
                plan_error_count += count_dict.get("error_count")
        test_plan_report['totalCount'] = plan_total_count
        test_plan_report['passCount'] = plan_pass_count
        test_plan_report['failCount'] = plan_fail_count
        test_plan_report['errorCount'] = plan_error_count
        plan_end_time = time.time()
        test_plan_report['spendTimeInSec'] = round(plan_end_time - plan_start_time, 3)
        test_plan_report['createAt'] = datetime.utcnow()
        save_plan_report(test_plan_report)
        if test_plan_report['totalCount'] > 0:
            notify_total_count = test_plan_report['totalCount']
            notify_pass_count = test_plan_report['passCount']
            notify_pass_rate = '{:.2%}'.format(notify_pass_count / notify_total_count)
            # 发送 邮件通知
            alarm_mail_list = []
            if alarm_mail_group_list:
                if isinstance(alarm_mail_group_list, list) and len(alarm_mail_group_list) > 0:
                    alarm_mail_list = get_mails_by_group(alarm_mail_group_list)
                else:
                    raise TypeError('alarm_mail_group_list must be list')
            is_send_mail = ((always_send_mail and isinstance(alarm_mail_list, list) and len(alarm_mail_list) > 0)
                            or (test_plan_report['totalCount'] > test_plan_report['passCount']
                                and isinstance(alarm_mail_list, list) and len(alarm_mail_list) > 0))
            if is_send_mail:
                subject = 'Leo API Auto Test Notify'
                content_plan_result = "<font color='green'>PASS</font>"
                if test_plan_report['totalCount'] > test_plan_report['passCount']:
                    content_plan_result = "<font color='red'>FAIL</font>"
                content = "<h2>Dears:</h2>" \
                          "<div style='font-size:20px'>&nbsp;&nbsp;API Test Plan executed successfully!<br/>" \
                          "&nbsp;&nbsp;Plan Name:&nbsp;&nbsp; <b>{}</b><br/>" \
                          "&nbsp;&nbsp;Environment:&nbsp;&nbsp; <b>{}</b><br/>" \
                          "&nbsp;&nbsp;Status:&nbsp;&nbsp; <b>{}</b><br/>" \
                          "&nbsp;&nbsp;TotalAPICount:&nbsp;&nbsp; <b>{}</b><br/>" \
                          "&nbsp;&nbsp;PassAPICount:&nbsp;&nbsp; <b>{}</b><br/>" \
                          "&nbsp;&nbsp;PassRate:&nbsp;&nbsp; <b>{}</b><br/>" \
                          "&nbsp;&nbsp;<a href=\"http://{}:{}/plan/{}/reportDetail/{}\">Please login platform " \
                          "for details!</a><br/>" \
                          "&nbsp;&nbsp;Report ID: {}<br/>" \
                          "&nbsp;&nbsp;Generated At: {} CST</div>" \
                    .format(plan_name, env_name, content_plan_result, notify_total_count, notify_pass_count,
                            notify_pass_rate, host_ip, host_port, plan_id, plan_report_id, plan_report_id,
                            test_plan_report['createAt'].replace(tzinfo=pytz.utc).astimezone(
                                pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S'))
                mail_result = send_cron_email(alarm_mail_list, subject, content)
                if mail_result.get('status') == 'failed':
                    with app.app_context():
                        current_app.logger.error('邮件发送异常: {}'.format(mail_result.get('data')))
                    raise BaseException('邮件发送异常: {}'.format(mail_result.get('data')))

            # 发送企业微信通知
            if enable_wxwork_notify:
                if always_wxwork_notify or test_plan_report['totalCount'] > test_plan_report['passCount']:
                    notify_title = 'Leo API Auto Test Notify'
                    content_plan_result = "<font color='green'>PASS</font>"
                    if test_plan_report['totalCount'] > test_plan_report['passCount']:
                        content_plan_result = "<font color='red'>FAIL</font>"
                    content_text = '''请注意'''
                    content_markdown = '''{} 
                    > Dears:
                        API Test Plan executed successfully!
                        Plan Name: **{}**
                        Environment: **{}**
                        Status: **{}**
                        TotalAPICount: **{}**
                        PassAPICount: **{}**
                        PassRate: **{}**
                        [Please login platform for details!](http://{}:{}/plan/{}/reportDetail/{})
                        Report ID: {}
                        Generated At: {} CST
                        '''.format(notify_title, plan_name, env_name, content_plan_result, notify_total_count,
                                   notify_pass_count,
                                   notify_pass_rate,
                                   host_ip, host_port, plan_id, plan_report_id, plan_report_id,
                                   test_plan_report['createAt'].replace(tzinfo=pytz.utc).astimezone(
                                       pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S'))
                    if mentioned_mobile_list and len(mentioned_mobile_list) > 0:
                        notify_res_text = send_notify.send_wxwork_notify_text(content_text, mentioned_mobile_list,
                                                                              wxwork_api_key)
                        if notify_res_text.status_code != 200 or eval(
                                str(notify_res_text.content, encoding="utf-8")).get('errcode') != 0:
                            with app.app_context():
                                current_app.logger.error('企业微信通知发送异常: ResponseCode:{}, ResponseBody:{}'.format(
                                    notify_res_text.status_code, notify_res_text.content))
                            raise BaseException('企业微信通知发送异常: ResponseCode:{}, ResponseBody:{}'.format(
                                notify_res_text.status_code, notify_res_text.content))
                    notify_res_markdown = send_notify.send_wxwork_notify_markdown(content_markdown, wxwork_api_key)
                    if notify_res_markdown.status_code != 200 or eval(
                            str(notify_res_markdown.content, encoding="utf-8")).get('errcode') != 0:
                        with app.app_context():
                            current_app.logger.error('企业微信通知发送异常: ResponseCode:{}, ResponseBody:{}'.format(
                                notify_res_markdown.status_code, notify_res_markdown.content))
                        raise BaseException('企业微信通知发送异常: ResponseCode:{}, ResponseBody:{}'.format(
                            notify_res_markdown.status_code, notify_res_markdown.content))

            # 发送钉钉通知
            if enable_ding_talk_notify:
                if always_ding_talk_notify or test_plan_report['totalCount'] > test_plan_report['passCount']:
                    notify_title = 'LEO API Auto Test Notify'
                    content_plan_result = "<font color='#00FF00'>PASS</font>"
                    if test_plan_report['totalCount'] > test_plan_report['passCount']:
                        content_plan_result = "<font color='#FF0000'>FAIL</font>"
                    content = "# {}\n" \
                              "API Test Plan executed successfully!\n\n" \
                              " Plan Name: **{}** \n\n" \
                              " Environment: **{}** \n\n" \
                              " Status: **{}** \n\n" \
                              " TotalAPICount: **{}** \n\n" \
                              " PassAPICount: **{}** \n\n" \
                              " PassRate: **{}** \n\n" \
                              " [Please login platform for details!](http://{}:{}/plan/{}/reportDetail/{})\n\n" \
                              " Report ID: **{}** \n\n" \
                              " Generated At: **{}** CST\n\n".format(notify_title, plan_name, env_name,
                                                                     content_plan_result, notify_total_count,
                                                                     notify_pass_count,
                                                                     notify_pass_rate,
                                                                     host_ip, host_port, plan_id, plan_report_id,
                                                                     plan_report_id,
                                                                     test_plan_report['createAt'].replace(
                                                                         tzinfo=pytz.utc).astimezone(
                                                                         pytz.timezone('Asia/Shanghai')).strftime(
                                                                         '%Y-%m-%d %H:%M:%S'))
                    notify_res = send_notify.send_ding_talk_notify_markdown(notify_title, content,
                                                                            ding_talk_access_token,
                                                                            at_mobiles=ding_talk_at_mobiles,
                                                                            secret=ding_talk_secret)
                    if notify_res.status_code != 200 or eval(str(notify_res.content, encoding="utf-8")).get(
                            'errcode') != 0:
                        with app.app_context():
                            current_app.logger.error('钉钉通知发送异常: ResponseCode:{}, ResponseBody:{}'.format(
                                notify_res.status_code, notify_res.content))
                        raise BaseException('钉钉通知发送异常: ResponseCode:{}, ResponseBody:{}'.format(
                            notify_res.status_code, notify_res.content))
        else:
            raise TypeError('无任何测试结果！')
    except BaseException as e:
        with app.app_context():
            current_app.logger.error("execute_plan_async exception - %s." % str(e))
        return False, "出错了 - %s" % e


def execute_single_project(item, plan_report_id, test_env_id, env_name, protocol, domain, execution_mode):
    # 根据时间生成一个ObjectId作为reportId
    project_report_id = str(ObjectId())
    project_start_datetime = datetime.utcnow()
    project_test_report = {
        '_id': ObjectId(project_report_id),
        'testEnvId': ObjectId(test_env_id),
        'testEnvName': env_name,
        'testStartTime': project_start_datetime,
        'executionMode': execution_mode,
        'projectId': ObjectId(item.get('projectId')),
        'planReportId': ObjectId(plan_report_id),
        'testSuites': {}
    }
    project_report_total_count = 0
    project_report_pass_count = 0
    project_report_fail_count = 0
    project_report_error_count = 0
    project_start_time = time.time()
    for test_suite_id in item.get("testSuiteIdList"):
        global_env_vars = get_global_env_vars(test_env_id)
        execute_engine = ExecutionEngine(test_env_id=test_env_id, protocol=protocol, domain=domain,
                                         global_env_vars=global_env_vars)
        test_suite_result = execute_engine.execute_single_suite_test(project_report_id, test_suite_id)
        project_test_report['testSuites'][test_suite_id] = test_suite_result
        project_report_total_count += test_suite_result['totalCount']
        project_report_pass_count += test_suite_result['passCount']
        project_report_fail_count += test_suite_result['failCount']
        project_report_error_count += test_suite_result['errorCount']
    project_test_report['totalCount'] = project_report_total_count
    project_test_report['passCount'] = project_report_pass_count
    project_test_report['failCount'] = project_report_fail_count
    project_test_report['errorCount'] = project_report_error_count
    project_end_time = time.time()
    project_test_report['spendTimeInSec'] = round(project_end_time - project_start_time, 3)
    project_test_report['createAt'] = datetime.utcnow()
    save_report(project_test_report)
    return {
        'total_count': project_report_total_count,
        'pass_count': project_report_pass_count,
        'fail_count': project_report_fail_count,
        'error_count': project_report_error_count
    }


def get_project_execution_range(range):
    # get execution range by priority for project
    if range.get("projectId") is None or range.get("priority") is None:
        with app.app_context():
            current_app.logger.error("ProjectId and Priority should not be empty.")
    if range.get("priority") == "P1" or range.get("priority") == "P2":
        query_dict = {'projectId': ObjectId(range.get("projectId")),
                      'priority': range.get("priority"),
                      'isDeleted': {"$ne": True},
                      'status': True}
    else:
        query_dict = {'projectId': ObjectId(range.get("projectId")), 'isDeleted': {"$ne": True}, 'status': True}
    res = TestSuite.find(query_dict)
    test_suite_id_list = list(map(lambda e: str(e.get('_id')), res))
    return {"projectId": range.get("projectId"), "testSuiteIdList": test_suite_id_list}


if __name__ == '__main__':
    pass
