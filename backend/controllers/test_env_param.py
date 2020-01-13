from datetime import datetime

from bson import ObjectId
from flask import jsonify, request, current_app
from flask_security import login_required

from app import app
from models.test_env_param import TestEnvParam
from utils import common


@app.route('/api/project/<project_id>/testEnv/<test_env_id>/paramList', methods=['GET'])
@login_required
def tet_env_param_list(project_id, test_env_id):
    total_num, param_list = common.get_total_num_and_arranged_data(TestEnvParam, request.args, fuzzy_fields=['name'])
    return jsonify({'status': 'ok', 'data': {'totalNum': total_num, 'rows': param_list}})


@app.route('/api/project/<project_id>/testEnv/<test_env_id>/addParam', methods=['POST'])
@login_required
def add_test_env_param(project_id, test_env_id):
    try:
        request_data = request.get_json()
        request_data['status'] = True
        request_data['projectId'] = ObjectId(project_id)
        request_data['testEnvId'] = ObjectId(test_env_id)
        request_data['createAt'] = datetime.utcnow()
        filtered_data = TestEnvParam.filter_field(request_data, use_set_default=True)
        TestEnvParam.insert(filtered_data)
        return jsonify({'status': 'ok', 'data': '新建成功'})
    except BaseException as e:
        current_app.logger.error("add_test_env_param failed. - %s" % str(e))
        return jsonify({'status': 'failed', 'data': '新建失败 %s' % e})


@app.route('/api/project/<project_id>/testEnv/updateParam/<test_env_param_id>', methods=['POST'])
@login_required
def update_test_env_param(project_id, test_env_param_id):
    try:
        request_data = request.get_json()
        request_data['lastUpdateTime'] = datetime.utcnow()
        filtered_data = TestEnvParam.filter_field(request_data)
        update_response = TestEnvParam.update({'_id': ObjectId(test_env_param_id)}, {'$set': filtered_data})
        if update_response['n'] == 0:
            return jsonify({'status': 'failed', 'data': '未找到相应的更新数据！'})
        return jsonify({'status': 'ok', 'data': '更新成功'})
    except BaseException as e:
        current_app.logger.error("update_test_env_param failed. - %s" % str(e))
        return jsonify({'status': 'failed', 'data': '更新失败 %s' % e})


def get_global_env_vars(test_env_id):
    global_env_vars = {}
    if test_env_id:
        for param in TestEnvParam.find(
                {'testEnvId': ObjectId(test_env_id), 'isDeleted': {'$ne': True}, 'status': True}):
            param_dict = common.format_response_in_dic(param)
            if param_dict.get('name') and param_dict.get('paramValue'):
                global_env_vars[param_dict.get('name')] = param_dict.get('paramValue')
    return global_env_vars
