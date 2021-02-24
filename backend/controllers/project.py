from datetime import datetime

from bson import ObjectId
from flask import jsonify, request, current_app
from flask_security import login_required, roles_accepted, current_user

from app import app
from models.project import Project
from models.test_suite import TestSuite
from models.test_case import TestCase
from utils import common


@app.route('/api/project/projectList', methods=['GET'])
@login_required
def project_list():
    total_num, projects = common.get_total_num_and_arranged_data(Project, request.args, fuzzy_fields=['name'])
    return jsonify({'status': 'ok', 'data': {'totalNum': total_num, 'rows': projects}})


@app.route('/api/project/<project_id>', methods=['GET'])
@login_required
def get_project(project_id):
    res = Project.find_one({'_id': ObjectId(project_id)})
    return jsonify({'status': 'ok', 'data': common.format_response_in_dic(res)})


@app.route('/api/project/addProject', methods=['POST'])
@login_required
@roles_accepted('admin', 'project')
def add_project():
    try:
        params = request.get_json()
        params['createAt'] = datetime.utcnow()
        filtered_data = Project.filter_field(params, use_set_default=True)
        Project.insert(filtered_data)
        current_app.logger.info(
            "add project successfully. Project: {}, User: {}".format(str(filtered_data['name']), current_user.email))
        return jsonify({'status': 'ok', 'data': '新建成功'})
    except BaseException as e:
        current_app.logger.error("add project failed. User:{}, Error:{}".format(current_user.email, str(e)))
        return jsonify({'status': 'failed', 'data': '新建失败 %s' % e})


@app.route('/api/project/<project_id>/updateProject', methods=['POST'])
@login_required
@roles_accepted('admin', 'project')
def update_project(project_id):
    try:
        request_data = request.get_json()
        request_data['lastUpdateTime'] = datetime.utcnow()
        filtered_data = Project.filter_field(request_data)
        if 'isDeleted' in filtered_data and filtered_data['isDeleted']:
            delete_project(project_id)
            return jsonify({'status': 'ok', 'data': '删除成功'})
        update_response = Project.update({'_id': ObjectId(project_id)}, {'$set': filtered_data})
        if update_response["n"] == 0:
            return jsonify({'status': 'failed', 'data': '未找到相应更新数据！'})
        current_app.logger.info(
            "update project successfully. Project: {}, User: {}".format(str(project_id), current_user.email))
        return jsonify({'status': 'ok', 'data': '更新成功'})
    except BaseException as e:
        current_app.logger.error("update project failed. User:{}, Error:{}".format(current_user.email, str(e)))
        return jsonify({'status': 'failed', 'data': '更新失败: %s' % e})


def delete_project(project_id):
    try:
        if not project_id:
            raise ValueError("project_id is empty!")
        delete_suites_count = 0
        delete_cases_count = 0
        Project.update({'_id': ObjectId(project_id)}, {'$set': {'isDeleted': True}})
        query = dict()
        query["projectId"] = ObjectId(project_id)
        total_num, test_suites = common.get_total_num_and_arranged_data(TestSuite, query)
        update_suite_response = TestSuite.update_many({'projectId': ObjectId(project_id)},
                                                      {'$set': {'isDeleted': True}})
        delete_suites_count += update_suite_response.modified_count
        for test_suite in test_suites:
            update_case_response = TestCase.update_many({'testSuiteId': ObjectId(test_suite['_id'])},
                                                        {'$set': {'isDeleted': True}})
            delete_cases_count += update_case_response.modified_count
        with app.app_context():
            current_app.logger.info(
                "Delete project successfully. ProjectId:{}, Deleted Test Suites Count:{}, "
                "Deleted Test Cases Count:{}, User:{}".format(project_id, delete_suites_count, delete_cases_count,
                                                              current_user.email))
    except BaseException as e:
        with app.app_context():
            current_app.logger.error("delete project failed. User:{}, error:{}".format(current_user.email, str(e)))
        raise BaseException(str(e))
