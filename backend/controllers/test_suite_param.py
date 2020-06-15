from datetime import datetime

from bson import ObjectId
from flask import jsonify, request, current_app
from flask_security import login_required

from app import app
from models.test_suite_param import TestSuiteParam
from utils import common


# Not yet used

@app.route('/api/project/<project_id>/testEnv/<test_env_id>/paramList', methods=['GET'])
@login_required
def tet_suite_param_list(project_id, test_suite_id):
    total_num, param_list = common.get_total_num_and_arranged_data(TestSuiteParam, request.args, fuzzy_fields=['name'])
    return jsonify({'status': 'ok', 'data': {'totalNum': total_num, 'rows': param_list}})


@app.route('/api/project/<project_id>/testSuite/<test_suite_id>/addParam', methods=['POST'])
@login_required
def add_test_suite_param(project_id, test_suite_id):
    try:
        request_data = request.get_json()
        request_data['status'] = True
        request_data['projectId'] = ObjectId(project_id)
        request_data['testSuiteId'] = ObjectId(test_suite_id)
        request_data['createAt'] = datetime.utcnow()
        filtered_data = TestSuiteParam.filter_field(request_data, use_set_default=True)
        TestSuiteParam.insert(filtered_data)
        return jsonify({'status': 'ok', 'data': '新建成功'})
    except BaseException as e:
        current_app.logger.error("add_test_suite_param failed. - %s" % str(e))
        return jsonify({'status': 'failed', 'data': '新建失败 %s' % e})


@app.route('/api/project/<project_id>/testSuite/updateParam/<test_suite_param_id>', methods=['POST'])
@login_required
def update_test_suite_param(project_id, test_suite_param_id):
    try:
        request_data = request.get_json()
        request_data['lastUpdateTime'] = datetime.utcnow()
        filtered_data = TestSuiteParam.filter_field(request_data)
        update_response = TestSuiteParam.update({'_id': ObjectId(test_suite_param_id)}, {'$set': filtered_data})
        if update_response['n'] == 0:
            return jsonify({'status': 'failed', 'data': '未找到相应的更新数据！'})
        return jsonify({'status': 'ok', 'data': '更新成功'})
    except BaseException as e:
        current_app.logger.error("update_test_suite_param failed. - %s" % str(e))
        return jsonify({'status': 'failed', 'data': '更新失败 %s' % e})
