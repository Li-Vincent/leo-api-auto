#!/usr/bin/python
# -*- coding: utf-8 -*-
import copy
import json
from datetime import datetime
from io import BytesIO

import xlrd
import xlsxwriter
from bson import ObjectId
from flask import jsonify, request, current_app, send_file
from flask_security import login_required

from app import app
from controllers.env_config import get_env_name_and_domain
from controllers.test_env_param import get_global_env_vars
from execution_engine.execution import ExecutionEngine, execute_test_by_suite_async
from models.test_case import TestCase
from models.test_suite import TestSuite
from utils import common


@app.route('/api/project/<project_id>/testSuite/<test_suite_id>/testCaseList', methods=['GET'])
@login_required
def case_list(project_id, test_suite_id):
    try:
        total_num, test_cases = common.get_total_num_and_arranged_data(TestCase, request.args, fuzzy_fields=['name'])
        for test_case in test_cases:
            if "lastManualResult" in test_case and "status" in test_case['lastManualResult']:
                test_case['lastManualResult'] = {"status": test_case['lastManualResult']["status"]}
        return jsonify({'status': 'ok', 'data': {'totalNum': total_num, 'rows': test_cases}})
    except BaseException as e:
        current_app.logger.error("get case list failed. - %s" % str(e))
        return jsonify({'status': 'failed', 'data': 'get case list failed %s' % str(e)})


@app.route('/api/testCaseLastManualResult/<test_case_id>', methods=['GET'])
@login_required
def test_case_last_manual_result(test_case_id):
    res = TestCase.find_one({'_id': ObjectId(test_case_id)})
    test_case = common.format_response_in_dic(res)
    return jsonify(
        {'status': 'ok', 'data': test_case['lastManualResult']}) if test_case and 'lastManualResult' in test_case else \
        jsonify({'status': 'failed', 'data': '未找到用例或当前用例没有执行结果'})


@app.route('/api/project/<project_id>/testSuite/<test_suite_id>/addCase', methods=['POST'])
def add_case(project_id, test_suite_id):
    try:
        # 查询 sequence 最大值
        res = TestCase.find_one({'testSuiteId': ObjectId(test_suite_id)}, sort=[('sequence', -1)])
        request_data = request.get_json()
        request_data['sequence'] = 1 if (res is None) else res['sequence'] + 1
        request_data["status"] = True
        request_data["testSuiteId"] = ObjectId(test_suite_id)
        request_data["projectId"] = ObjectId(project_id)
        request_data["testCaseType"] = 'apiTest'
        request_data["createAt"] = datetime.utcnow()
        filtered_data = TestCase.filter_field(request_data, use_set_default=True)
        TestCase.insert(filtered_data)
        current_app.logger.info("add test case successfully. case name: %s" % str(filtered_data['name']))
        return jsonify({'status': 'ok', 'data': '添加成功'})
    except BaseException as e:
        current_app.logger.error("add_case failed. - %s" % str(e))
        return jsonify({'status': 'failed', 'data': '添加失败 %s' % e})


@app.route('/api/project/<project_id>/testSuite/<test_suite_id>/copyCase/<test_case_id>', methods=['POST'])
def copy_case(project_id, test_suite_id, test_case_id):
    # 查询 sequence 最大值
    try:
        res = TestCase.find_one({'_id': ObjectId(test_case_id)})
        if not res:
            current_app.logger.error('can not find test_case by id: %s' % test_case_id)
            return jsonify({'status': 'failed', 'data': '未找到要复制的test_case'})
        request_data = request.get_json()
        new_case_data = res
        # 去除_id
        new_case_data.pop('_id')
        if 'lastUpdateTime' in new_case_data:
            new_case_data.pop('lastUpdateTime')
        if 'lastUpdateUser' in new_case_data:
            new_case_data.pop('lastUpdateUser')
        if 'lastManualResult' in new_case_data:
            new_case_data.pop('lastManualResult')
        new_case_name_prefix = 'Copy - '
        new_case_name = new_case_name_prefix + new_case_data.pop('name') \
            if 'name' in new_case_data else new_case_name_prefix + 'Unknown Test Case'
        new_case_data['name'] = new_case_name
        new_case_data['sequence'] = new_case_data['sequence'] + 1
        new_case_data["status"] = True
        new_case_data["createAt"] = datetime.utcnow()
        new_case_data['createUser'] = request_data['createUser']
        filtered_data = TestCase.filter_field(new_case_data, use_set_default=True)
        TestCase.insert(filtered_data)
        current_app.logger.info("copy test case successfully. new case name: %s" % str(new_case_name))
        return jsonify({'status': 'ok', 'data': '复制成功'})
    except BaseException as e:
        current_app.logger.error("copy_case failed. - %s" % str(e))
        return jsonify({'status': 'failed', 'data': '复制失败 %s' % e})


@app.route('/api/project/<project_id>/testSuite/<test_suite_id>/updateCase/<test_case_id>', methods=['POST'])
@login_required
def update_case(project_id, test_suite_id, test_case_id):
    request_data = request.get_json()
    if request_data.get('requestBody') is not None:
        if isinstance(request_data.get('requestBody'), str) and \
                request_data.get('requestBody').strip() == '':
            request_data['requestBody'] = [{}]
        else:
            try:
                request_data['requestBody'] = request_data['requestBody'].replace('\'', '\"')
                request_data['requestBody'] = json.loads(request_data['requestBody'])
                if isinstance(request_data['requestBody'], dict):
                    request_data['requestBody'] = [request_data['requestBody']]
                if not isinstance(request_data['requestBody'], list):
                    return jsonify({'status': 'failed', 'data': '请求参数数据格式不正确!'})
            except BaseException as e:
                current_app.logger.error("update_case failed. - %s" % str(e))
                return jsonify({'status': 'failed', 'data': '请求参数数据格式不正确!: %s' % e})
    try:
        request_data['lastUpdateTime'] = datetime.utcnow()
        filtered_data = TestCase.filter_field(request_data)
        update_response = TestCase.update({'_id': ObjectId(test_case_id)}, {'$set': filtered_data})
        if update_response["n"] == 0:
            return jsonify({'status': 'failed', 'data': '未找到相应更新数据！'})
        current_app.logger.info("update test case successfully. case ID: %s" % str(test_case_id))
        return jsonify({'status': 'ok', 'data': '更新成功'})
    except BaseException as e:
        current_app.logger.error("update_case failed. - %s" % str(e))
        return jsonify({'status': 'failed', 'data': '更新失败: %s' % e})


# 获取测试项目中的接口信息
@app.route('/api/project/<project_id>/testSuite/<test_suite_id>/testCase/<test_case_id>', methods=['GET', 'POST'])
@login_required
def test_case_detail(project_id, test_suite_id, test_case_id):
    res = TestCase.find_one({'_id': ObjectId(test_case_id)})
    test_case = common.format_response_in_dic(res)
    return jsonify({'status': 'ok', 'data': test_case}) if test_case else \
        jsonify({'status': 'failed', 'data': '未找到用例详情'})


@app.route('/api/startAPITestByCase', methods=['POST'])
@login_required
def start_api_test_by_case():
    request_data = request.get_json()
    test_case_id_list = None
    execution_user = None
    execution_mode = None
    test_env_id = None

    if 'testEnvId' not in request_data:
        return jsonify({'status': 'failed', 'data': '尚未选择环境！'})
    else:
        test_env_id = request_data["testEnvId"]

    if 'testCaseIdList' in request_data:
        test_case_id_list = request_data["testCaseIdList"]

    if not test_case_id_list or len(test_case_id_list) < 1:
        return jsonify({'status': 'failed', 'data': '请选择接口测试用例'})

    if 'executionUser' in request_data:
        execution_user = request_data["executionUser"]

    if 'executionMode' in request_data:
        execution_mode = request_data["executionMode"]

    testing_case_list = []
    for test_case_id in test_case_id_list:
        testing_case = TestCase.find_one({'_id': ObjectId(test_case_id), 'isDeleted': {'$ne': True}, 'status': True})
        if testing_case:
            testing_case_list.append(common.format_response_in_dic(testing_case))

    if len(testing_case_list) < 1:
        return jsonify({'status': 'failed', 'data': '未找到任何「启用的」接口测试用例'})

    # 去除相同的测试用例
    def remove_duplicated_case(case_list):
        id_list = []
        for case in case_list:
            case_id = case["_id"]
            if case_id in id_list:
                case_list.remove(case)
            else:
                id_list.append(case_id)
        return case_list

    testing_case_list = remove_duplicated_case(testing_case_list)

    (env_name, protocol, domain) = get_env_name_and_domain(test_env_id)
    if not protocol or not domain or not env_name:
        return jsonify({'status': 'failed', 'data': '测试环境配置存在问题，请前往环境设置检查'})

    global_env_vars = get_global_env_vars(test_env_id)

    execute_engine = ExecutionEngine(test_env_id=test_env_id, protocol=protocol, domain=domain,
                                     global_env_vars=global_env_vars)

    test_result_list = execute_engine.execute_manual_test_by_case(testing_case_list)
    try:
        for test_result in test_result_list:
            test_case_id = test_result["_id"]
            if execution_user:
                test_result['executionUser'] = execution_user
            test_result['env'] = env_name
            test_result = common.format_response_in_dic(test_result)
            TestCase.update({"_id": ObjectId(test_case_id)},
                            {'$set': {'lastManualResult': test_result}})
        return jsonify({'status': 'ok', 'data': "执行完毕"})
    except BaseException as e:
        current_app.logger.error("start_api_test_by_case failed. - %s" % str(e))
        return jsonify({'status': 'failed', 'data': "出错了 - %s" % e})


@app.route('/api/startAPITestBySuite', methods=['POST'])
@login_required
def start_api_test_by_suite():
    request_data = request.get_json()
    execution_user = None
    if 'testEnvId' not in request_data:
        return jsonify({'status': 'failed', 'data': '尚未选择环境！'})
    else:
        test_env_id = request_data["testEnvId"]

    if 'projectId' in request_data:
        project_id = request_data['projectId']

    if 'testSuiteIdList' in request_data:
        test_suite_id_list = request_data["testSuiteIdList"]

    if not test_suite_id_list or len(test_suite_id_list) < 1:
        return jsonify({'status': 'failed', 'data': '未找到任何「启用的」用例组'})

    execution_mode = request_data["executionMode"]
    if execution_mode == 'manual':
        execution_user = request_data["executionUser"]

    (env_name, protocol, domain) = get_env_name_and_domain(test_env_id)
    if not protocol or not domain or not env_name:
        return jsonify({'status': 'failed', 'data': '测试环境配置存在问题，请前往环境设置检查'})

    global_env_vars = get_global_env_vars(test_env_id)

    # 根据时间生成一个ObjectId作为reportId
    report_id = str(common.get_object_id())
    test_report = {'_id': ObjectId(report_id),
                   'testEnvId': ObjectId(test_env_id),
                   'testEnvName': env_name,
                   'executionMode': execution_mode}
    if execution_user:
        test_report['executionUser'] = execution_user
    if project_id:
        test_report['projectId'] = ObjectId(project_id)
    try:
        execute_test_by_suite_async(report_id, test_report, test_env_id, test_suite_id_list, protocol, domain,
                                    global_env_vars)
        return jsonify({'status': 'ok', 'data': "测试已成功启动，请稍后前往「测试报告」查看报告"})
    except BaseException as e:
        current_app.logger.error("start_api_test_by_suite failed. - %s" % str(e))
        return jsonify({'status': 'failed', 'data': "出错了 - %s" % e})


test_case_map = {
    'testSuiteId': '用例组_id',
    'testSuiteName': '用例组名称',
    '_id': '用例_id',
    'name': '用例名称',
    'description': '用例描述',
    'sequence': '执行顺序',

    'requestProtocol': '请求协议',
    'requestMethod': '请求方法',
    'domain': '请求域名',
    'service': '服务名',
    'route': '请求路由',
    'headers': '请求头部',
    'isClearCookie': '请求前是否清除Cookie',
    'dataInitializes': '数据初始化',
    'requestBody': '请求参数',
    'setGlobalVars': '设置全局变量',

    'checkResponseCode': '返回状态码校验',
    'checkResponseBody': '返回结果校验',
    'checkResponseNumber': '数值计算校验',

    'createAt': '创建时间/UTC',
    'createUser': '创建人',
    'lastUpdateTime': '最后更新时间/UTC',
    'lastUpdateUser': '最后更新人',
}

# export cases sort by
_sort_query = [('testSuiteId', 1), ('sequence', 1), ('createAt', 1)]


@app.route("/api/importTestCases", methods=['POST'])
@login_required
def import_test_cases():
    file = request.files.get('file')
    request_data = request.form
    current_test_suite_id = request_data.get('testSuiteId') if request_data else None
    project_id = request_data.get('projectId') if request_data else None
    current_user = request_data.get('user') if request_data else None

    if file is None or project_id is None or current_user is None:
        return jsonify({'status': 'failed', 'data': '参数不合法！值为: None'})

    if current_test_suite_id == 'undefined' or project_id == 'undefined' or current_user == 'undefined':
        return jsonify({'status': 'failed', 'data': '参数不合法！值为: undefined'})

    try:
        file_content = file.read()
        workbook = xlrd.open_workbook(file_contents=file_content)
    except BaseException as e:
        return jsonify({'status': 'failed', 'data': '「Excel」读取失败! %s' % e})

    if '测试用例' not in workbook.sheet_names():
        return jsonify({'status': 'failed', 'data': '「Excel」缺失「测试用例」Sheet'})

    test_case_table = workbook.sheet_by_name('测试用例')
    rows_num = test_case_table.nrows  # 获取该sheet中的有效行数

    if rows_num < 2:
        return jsonify({'status': 'failed', 'data': '「测试用例」Sheet 有效行数小于两行: %s 行' % rows_num})

    # 获取表头
    test_case_attributes = test_case_table.row_values(0)

    # 获取表头和case_map的差集
    diff_list = list(set(test_case_map.values()) ^ set(test_case_attributes))

    # 如果表头和case_map不一致则报错
    if diff_list:
        missing_attributes = [diff for diff in diff_list if diff in test_case_map.values()]
        extra_attributes = [diff for diff in diff_list if diff not in test_case_map.values()]
        fail_msg = ''
        if missing_attributes:
            fail_msg += '「测试用例」Sheet 表头缺失字段: %s\n' % missing_attributes
        if extra_attributes:
            fail_msg += '「测试用例」Sheet 表头存在多余字段: %s\n' % extra_attributes
        if fail_msg:
            return jsonify({'status': 'failed', 'data': fail_msg})

    attributes_indexes = [test_case_attributes.index(v) for v in test_case_map.values()]

    # TODO:
    def get_pre_import_case_info(case_info, test_case_mapping, table_row_index):
        _is_test_case_exist, _case_info, _is_test_suite_exist = \
            common.validate_and_pre_process_import_test_case(TestSuite, TestCase, case_info,
                                                             test_case_mapping, table_row_index)
        return _is_test_case_exist, _case_info, _is_test_suite_exist

    results = []
    import_count = 0
    update_count = 0
    test_case_info = copy.deepcopy(test_case_map)
    for i in range(1, rows_num):
        for k, v in enumerate(test_case_info.keys()):
            test_case_info[v] = test_case_table.row_values(i)[attributes_indexes[k]]
        try:
            # is_case_exist, pre_import_case_info, is_case_suite_exist \
            #     = get_pre_import_case_info(test_case_info, test_case_mapping=test_case_map, table_row_index=(i + 2))
            is_test_case_exist, pre_import_case_info, is_test_suite_exist = common.validate_and_pre_process_import_test_case(
                TestSuite, TestCase, test_case_info, test_case_map, i + 1)
        except BaseException as b_e:
            return jsonify({'status': 'failed', 'data': '导入数据异常: %s' % b_e})

        try:
            # 在用例列表中导入
            if current_test_suite_id:
                if is_test_case_exist and str(pre_import_case_info.get('testSuiteId')) == str(current_test_suite_id):
                    pre_import_case_info = TestCase.filter_field(pre_import_case_info, use_set_default=False)
                    result = str(TestCase.update({"_id": ObjectId(pre_import_case_info.get('_id'))},
                                                 {'$set': pre_import_case_info})) + ' _id: {}'.format(
                        pre_import_case_info.get('_id'))
                    update_count += 1
                else:
                    try:
                        pre_import_case_info.pop('_id') if '_id' in pre_import_case_info else None
                    except BaseException as e:
                        pass
                    pre_import_case_info['status'] = True
                    pre_import_case_info['testSuiteId'] = ObjectId(current_test_suite_id)
                    pre_import_case_info['projectId'] = ObjectId(project_id)
                    pre_import_case_info['createUser'] = current_user
                    pre_import_case_info['lastUpdateUser'] = current_user
                    pre_import_case_info['testCaseType'] = 'apiTest'
                    pre_import_case_info = TestCase.filter_field(pre_import_case_info, use_set_default=True)
                    result = TestCase.insert(pre_import_case_info)
                    import_count += 1
            # 在用例组列表内导入
            else:
                inserted_test_suite_id = None
                test_suite_name = pre_import_case_info.get('testSuiteName') \
                    if pre_import_case_info.get('testSuiteName') else ''
                if is_test_suite_exist:
                    if not test_suite_name == \
                           TestSuite.find_one({"_id": ObjectId(pre_import_case_info.get('testSuiteId'))})['name']:
                        TestSuite.update({"_id": ObjectId(pre_import_case_info.get('testSuiteId'))},
                                         {'$set': {'name': test_suite_name}})
                    else:
                        pass
                else:
                    insert_data = dict()
                    insert_data["name"] = test_suite_name
                    insert_data["status"] = True
                    insert_data["projectId"] = ObjectId(project_id)
                    insert_data["lastUpdateTime"] = datetime.utcnow()
                    insert_data["createAt"] = datetime.utcnow()
                    insert_data["createUser"] = current_user
                    insert_data["lastUpdateUser"] = current_user
                    inserted_test_suite_id = TestSuite.insert(insert_data)

                if inserted_test_suite_id:
                    pre_import_case_info.pop('_id') if is_test_case_exist else None
                    pre_import_case_info["projectId"] = ObjectId(project_id)
                    pre_import_case_info['testSuiteId'] = ObjectId(inserted_test_suite_id)
                    pre_import_case_info = TestCase.filter_field(pre_import_case_info, use_set_default=True)
                    result = TestCase.insert(pre_import_case_info)
                    import_count += 1

                else:
                    if is_test_case_exist:
                        pre_import_case_info = TestCase.filter_field(pre_import_case_info, use_set_default=False)
                        result = str(TestCase.update({"_id": ObjectId(pre_import_case_info.get('_id'))},
                                                     {'$set': pre_import_case_info})) + ' _id: {}'.format(
                            pre_import_case_info.get('_id'))
                        update_count += 1
                    else:
                        pre_import_case_info["projectId"] = ObjectId(project_id)
                        pre_import_case_info['testSuiteId'] = ObjectId(pre_import_case_info.get('testSuiteId'))
                        pre_import_case_info = TestCase.filter_field(pre_import_case_info, use_set_default=True)
                        result = TestCase.insert(pre_import_case_info)
                        import_count += 1

            results.append(result)
        except BaseException as e:
            return jsonify({'status': 'failed', 'data': '数据导入异常: %s' % e})

    def get_returned_data(_results, _import_count, _update_count):
        _returned_data = dict()
        _returned_data['status'] = 'ok'
        if import_count > 0 and update_count == 0:
            _returned_data['data'] = '操作成功, 共成功导入 %s 条用例' % _import_count
            # _returned_data['log'] = '导入数据_id: %s' % _results
        elif update_count > 0 and import_count == 0:
            _returned_data['data'] = '操作成功, 共成功覆盖 %s 条用例' % _update_count
            # _returned_data['log'] = '导入数据_id: %s' % _results
        elif import_count > 0 and update_count > 0:
            _returned_data['data'] = '操作成功, 共成功导入 %s 条用例、覆盖 %s 条用例' % (import_count, update_count)
            # _returned_data['log'] = '导入数据_id: %s' % _results
        else:
            _returned_data['data'] = '操作成功，但啥都没导入 / 覆盖'
            # _returned_data['log'] = None
        return jsonify(_returned_data)

    returned_data = get_returned_data(results, import_count, update_count)
    return returned_data


@app.route('/api/exportTestCases', methods=['POST'])
@login_required
def export_test_cases():
    request_data = request.get_json()

    def is_list_valid(input_data):
        is_valid = isinstance(input_data, list) and len(input_data) > 0
        return is_valid

    test_case_ids = request_data.get('testCaseIds') if is_list_valid(request_data.get('testCaseIds')) else []
    test_suite_ids = request_data.get('testSuiteIds') if is_list_valid(request_data.get('testSuiteIds')) else []

    if not test_case_ids and not test_suite_ids:
        return jsonify({'status': 'failed', 'data': '参数不合法!'})

    try:
        test_case_ids = list(map(lambda x: ObjectId(x), test_case_ids))
        test_suite_ids = list(map(lambda x: ObjectId(x), test_suite_ids))
    except BaseException as e:
        return jsonify({'status': 'failed', 'data': '参数不合法: %s' % e})

    query = {
        '$or': [
            {'_id': {'$in': test_case_ids}, 'isDeleted': {'$ne': True}},
            {'testSuiteId': {'$in': test_suite_ids}, 'isDeleted': {'$ne': True}}
        ]
    }

    def export_case_format(case):
        export_case = list()
        for key in test_case_map.keys():
            if isinstance(case.get(key), list):
                case_data = common.LIST_SEPARATOR.join(
                    ([str(x) if common.can_convert_to_str(x) else '' for x in case[key]]))
            elif isinstance(case.get(key), datetime):
                case_data = str(case.get(key)).replace('.', ':', 1) if common.can_convert_to_str(case.get(key)) and str(
                    case.get(key)).count('.') < 2 else str(case.get(key))
            else:
                case_data = str(case.get(key)) if case.get(key) is not None else ''
            export_case.append(case_data)
        return export_case

    def add_test_suite_name(case_info):
        _case_suite_id = case_info.get('testSuiteId')
        try:
            test_suite_name = TestSuite.find_one({'_id': _case_suite_id})['name'] \
                if TestSuite.find_one({'_id': _case_suite_id}) else ''
            case_info['testSuiteName'] = test_suite_name if test_suite_name else ''
        except BaseException as e:
            print(e)
        return case_info

    _export_test_cases = list(
        map(export_case_format, list(map(add_test_suite_name, TestCase.find(query, sort=_sort_query)))))
    bytes_io = BytesIO()
    workbook = xlsxwriter.Workbook(bytes_io, {'in_memory': True})
    sheet = workbook.add_worksheet(u'测试用例')

    for index, value in enumerate(test_case_map.values()):
        sheet.write(0, index, value)
    for row_index, values in enumerate(_export_test_cases):
        for col_index, value in enumerate(values):
            sheet.write(row_index + 1, col_index, value)

    workbook.close()
    bytes_io.seek(0)
    # return .xlsx
    return send_file(bytes_io, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
