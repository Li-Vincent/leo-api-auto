import json
from datetime import datetime

from bson import ObjectId
from flask import jsonify, request
from flask_security import login_required

from app_init import app
from controllers.test_env import get_env_name_and_domain
from controllers.test_env_param import get_global_env_vars
from execution_engine.execution import ExecutionEngine, execute_test_by_suite_async
from models.test_case import TestCase
from utils import common


@app.route('/api/project/<project_id>/testSuite/<test_suite_id>/testCaseList', methods=['GET'])
@login_required
def case_list(project_id, test_suite_id):
    total_num, test_cases = common.get_total_num_and_arranged_data(TestCase, request.args, fuzzy_fields=['name'])
    return jsonify({'status': 'ok', 'data': {'totalNum': total_num, 'rows': test_cases}})


@app.route('/api/project/<project_id>/testSuite/<test_suite_id>/addCase', methods=['POST'])
def add_case(project_id, test_suite_id):
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
    try:
        TestCase.insert(filtered_data)
        return jsonify({'status': 'ok', 'data': '添加成功'})
    except BaseException as e:
        return jsonify({'status': 'failed', 'data': '添加失败 %s' % e})


@app.route('/api/project/<project_id>/testSuite/<test_suite_id>/updateCase/<test_case_id>', methods=['POST'])
@login_required
def update_case(project_id, test_suite_id, test_case_id):
    request_data = request.get_json()
    print(request_data)
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
                return jsonify({'status': 'failed', 'data': '请求参数数据格式不正确!: %s' % e})
    try:
        request_data['lastUpdateTime'] = datetime.utcnow()
        filtered_data = TestCase.filter_field(request_data)
        update_response = TestCase.update({'_id': ObjectId(test_case_id)}, {'$set': filtered_data})
        if update_response["n"] == 0:
            return jsonify({'status': 'failed', 'data': '未找到相应更新数据！'})
        return jsonify({'status': 'ok', 'data': '更新成功'})
    except BaseException as e:
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

    (env_name, domain) = get_env_name_and_domain(test_env_id)
    if not domain:
        return jsonify({'status': 'failed', 'data': '未找到任何「启用的」环境信息'})
    if not env_name:
        return jsonify({'status': 'failed', 'data': '测试环境名称为空，请设置环境名称'})

    global_env_vars = get_global_env_vars(test_env_id)

    execute_engine = ExecutionEngine(test_env_id=test_env_id, domain=domain, global_env_vars=global_env_vars)

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

    (env_name, domain) = get_env_name_and_domain(test_env_id)
    if not domain:
        return jsonify({'status': 'failed', 'data': '未找到任何「启用的」环境信息'})
    if not env_name:
        return jsonify({'status': 'failed', 'data': '测试环境名称为空，请设置环境名称'})

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
        execute_test_by_suite_async(report_id, test_report, test_env_id, test_suite_id_list, domain, global_env_vars)
        return jsonify({'status': 'ok', 'data': "触发执行完毕"})
    except BaseException as e:
        return jsonify({'status': 'failed', 'data': "出错了 - %s" % e})
