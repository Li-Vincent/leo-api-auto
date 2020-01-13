from datetime import datetime

from bson import ObjectId
from flask import jsonify, request, current_app
from flask_security import login_required

from app import app
from models.test_suite import TestSuite
from utils import common


@app.route('/api/project/<project_id>/testSuiteList', methods=['GET', 'POST'])
def test_suite_list(project_id):
    total_num, test_suites = common.get_total_num_and_arranged_data(TestSuite, request.args, fuzzy_fields=['name'])
    return jsonify({'status': 'ok', 'data': {'totalNum': total_num, 'rows': test_suites}})


@app.route('/api/project/<project_id>/testSuite/<test_suite_id>', methods=['GET'])
@login_required
def get_project_suite(project_id, test_suite_id):
    res = TestSuite.find_one({'_id': ObjectId(test_suite_id)})
    return jsonify({'status': 'ok', 'data': common.format_response_in_dic(res)})


@app.route('/api/project/<project_id>/addTestSuite', methods=['POST'])
def add_test_suite(project_id):
    request_data = request.get_json()
    request_data['projectId'] = ObjectId(project_id)
    request_data['status'] = True
    request_data['createAt'] = datetime.utcnow()
    try:
        filtered_data = TestSuite.filter_field(request_data, use_set_default=True)
        TestSuite.insert(filtered_data)
        return jsonify({'status': 'ok', 'data': '添加成功'})
    except BaseException as e:
        current_app.logger.error("add_test_suite failed. - %s" % str(e))
        return jsonify({'status': 'failed', 'data': '添加失败 % s' % e})


@app.route('/api/project/<project_id>/updateTestSuite/<test_suite_id>', methods=['POST'])
def update_test_suite(project_id, test_suite_id):
    try:
        request_data = request.get_json()
        request_data['lastUpdateTime'] = datetime.utcnow()
        filtered_data = TestSuite.filter_field(request_data)
        update_response = TestSuite.update({'_id': ObjectId(test_suite_id)}, {'$set': filtered_data})
        if update_response['n'] == 0:
            return jsonify({'status': 'failed', 'data': '未找到相应的更新数据！'})
        return jsonify({'status': 'ok', 'data': '更新成功'})
    except BaseException as e:
        current_app.logger.error("update_test_suite failed. - %s" % str(e))
        return jsonify({'status': 'failed', 'data': '更新失败 %s' % e})


@app.route('/api/project/<project_id>/copyTestSuite/<test_suite_id>')
def copy_test_suite(project_id, test_suite_id):
    try:
        test_case_suite = TestSuite.find_one({'_id': ObjectId(test_suite_id)})
        # TODO
        return jsonify({'status': 'ok', 'data': '复制成功'})
    except BaseException as e:
        current_app.logger.error("copy_test_suite failed. - %s" % str(e))
        return jsonify({'status': 'failed', 'data': '复制失败 %s' % e})


def get_suite_name(test_suite_id):
    if test_suite_id:
        test_suite = common.format_response_in_dic(TestSuite.find_one({'_id': ObjectId(test_suite_id)}))
        return test_suite['name']
    else:
        current_app.logger.error("get_suite_name failed. - %s" % str("test_suite_id is empty"))
        raise ValueError("test_suite_id should not be empty")
