from datetime import datetime

from bson import ObjectId
from flask import jsonify, request, current_app
from flask_security import login_required, current_user

from app import app
from models.test_suite import TestSuite
from models.test_case import TestCase
from utils import common


@app.route('/api/project/<project_id>/testSuiteList', methods=['GET', 'POST'])
@login_required
def test_suite_list(project_id):
    total_num, test_suites = common.get_total_num_and_arranged_data(TestSuite, request.args, fuzzy_fields=['name'])
    return jsonify({'status': 'ok', 'data': {'totalNum': total_num, 'rows': test_suites}})


@app.route('/api/project/<project_id>/testSuite/<test_suite_id>', methods=['GET'])
@login_required
def get_project_suite(project_id, test_suite_id):
    res = TestSuite.find_one({'_id': ObjectId(test_suite_id)})
    return jsonify({'status': 'ok', 'data': common.format_response_in_dic(res)})


@app.route('/api/project/<project_id>/addTestSuite', methods=['POST'])
@login_required
def add_test_suite(project_id):
    request_data = request.get_json()
    request_data['projectId'] = ObjectId(project_id)
    request_data['status'] = True
    request_data['createAt'] = datetime.utcnow()
    try:
        filtered_data = TestSuite.filter_field(request_data, use_set_default=True)
        TestSuite.insert(filtered_data)
        current_app.logger.info(
            "add_test_suite successfully. Name: {}, User:{}".format(str(filtered_data['name']), current_user.email))
        return jsonify({'status': 'ok', 'data': '添加成功'})
    except BaseException as e:
        current_app.logger.error("add_test_suite failed. User:{},Error:{}".format(current_user.email, str(e)))
        return jsonify({'status': 'failed', 'data': '添加失败 % s' % e})


@app.route('/api/project/<project_id>/updateTestSuite/<test_suite_id>', methods=['POST'])
@login_required
def update_test_suite(project_id, test_suite_id):
    try:
        request_data = request.get_json()
        request_data['lastUpdateTime'] = datetime.utcnow()
        filtered_data = TestSuite.filter_field(request_data)
        if 'isDeleted' in filtered_data and filtered_data['isDeleted']:
            delete_test_suites([test_suite_id])
            return jsonify({'status': 'ok', 'data': '删除成功'})
        update_response = TestSuite.update({'_id': ObjectId(test_suite_id)}, {'$set': filtered_data})
        if update_response['n'] == 0:
            return jsonify({'status': 'failed', 'data': '未找到相应的更新数据！'})
        current_app.logger.info(
            "update_test_suite successfully. ID: {}, User:{}".format(str(test_suite_id), current_user.email))
        return jsonify({'status': 'ok', 'data': '更新成功'})
    except BaseException as e:
        current_app.logger.error("update_test_suite failed. User:{}, Error:{}".format(current_user.email, str(e)))
        return jsonify({'status': 'failed', 'data': '更新失败 %s' % e})


@app.route('/api/project/<project_id>/copyTestSuite/<test_suite_id>', methods=['POST'])
@login_required
def copy_test_suite(project_id, test_suite_id):
    try:
        request_data = request.get_json()
        origin_test_suite = TestSuite.find_one({'_id': ObjectId(test_suite_id)})
        if not origin_test_suite:
            current_app.logger.error('can not find test_suite by id - %s' % test_suite_id)
            return jsonify({'status': 'failed', 'data': '未找到要复制的test_suite'})
        new_suite_name_prefix = 'Copy - '
        new_test_suite = origin_test_suite
        new_test_suite.pop('_id')
        if 'lastUpdateTime' in new_test_suite:
            new_test_suite.pop('lastUpdateTime')
        if 'lastUpdateUser' in new_test_suite:
            new_test_suite.pop('lastUpdateUser')
        new_suite_name = new_suite_name_prefix + new_test_suite.pop('name') \
            if 'name' in new_test_suite else new_suite_name_prefix + 'Unknown Test Suite'
        new_test_suite['name'] = new_suite_name
        new_test_suite["status"] = True
        new_test_suite["createAt"] = datetime.utcnow()
        new_test_suite['createUser'] = request_data['createUser']
        filtered_data = TestSuite.filter_field(new_test_suite, use_set_default=True)
        # insert new test suite
        new_test_suite_id = TestSuite.insert(filtered_data)

        # query test case
        query = {'testSuiteId': ObjectId(test_suite_id), 'isDeleted': {'$ne': True}}
        copied_test_cases = list(TestCase.find(query, sort=[('sequence', 1)]))

        def handle_copied_case(test_case):
            if 'lastUpdateTime' in test_case:
                test_case.pop('lastUpdateTime')
            if 'lastUpdateUser' in test_case:
                test_case.pop('lastUpdateUser')
            if 'lastManualResult' in test_case:
                test_case.pop('lastManualResult')
            test_case.pop('_id')
            test_case['testSuiteId'] = ObjectId(new_test_suite_id)
            test_case["createAt"] = datetime.utcnow()
            test_case['createUser'] = request_data['createUser']
            return test_case

        handled_test_cases = list(map(handle_copied_case, copied_test_cases))
        for handled_test_case in handled_test_cases:
            filtered_test_case = TestCase.filter_field(handled_test_case)
            TestCase.insert(filtered_test_case)
        current_app.logger.info(
            "copy_test_suite successfully. New Suite Name: {}, User:{}".format(str(new_suite_name), current_user.email))
        return jsonify({'status': 'ok', 'data': '复制成功'})
    except BaseException as e:
        current_app.logger.error("copy_test_suite failed. User:{}, Error:{}".format(current_user.email, str(e)))
        return jsonify({'status': 'failed', 'data': '复制失败 %s' % e})


def get_suite_name(test_suite_id):
    try:
        test_suite = common.format_response_in_dic(TestSuite.find_one({'_id': ObjectId(test_suite_id)}))
        return test_suite['name']
    except BaseException as e:
        with app.app_context():
            current_app.logger.error("get_suite_name failed. - %s" % str(e))
        return None


def delete_test_suites(test_suite_ids):
    try:
        if not isinstance(test_suite_ids, list):
            raise TypeError("test_suite_ids should be a list!")
        if len(test_suite_ids) < 1:
            raise ValueError("test_suite_ids is empty!")
        delete_count = 0
        for test_suite_id in test_suite_ids:
            TestSuite.update({'_id': ObjectId(test_suite_id)}, {'$set': {'isDeleted': True}})
            update_case_response = TestCase.update_many({'testSuiteId': ObjectId(test_suite_id)},
                                                        {'$set': {'isDeleted': True}})
            delete_count += update_case_response.modified_count
        with app.app_context():
            current_app.logger.info(
                "Delete test suites successfully. testSuiteIds:{}, Deleted Test Cases Count:{}, User:{}".format(
                    str(test_suite_ids), delete_count, current_user.email))
    except BaseException as e:
        with app.app_context():
            current_app.logger.error("delete test suites failed. User:{}, Error:{}".format(current_user.email, str(e)))
        raise BaseException(str(e))
