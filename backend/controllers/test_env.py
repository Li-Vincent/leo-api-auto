from datetime import datetime

from bson import ObjectId
from flask import jsonify, request
from flask_security import login_required, roles_required

from app import app
from models.test_env import TestEnv
from utils import common


@app.route('/api/project/<project_id>/testEnvList', methods=['GET'])
@login_required
def test_env_list(project_id):
    total_num, envs = common.get_total_num_and_arranged_data(TestEnv, request.args, fuzzy_fields=['name'])
    return jsonify({'status': 'ok', 'data': {'totalNum': total_num, 'rows': envs}})


@app.route('/api/project/<project_id>/testEnv/<test_env_id>', methods=['GET'])
@login_required
def get_project_env(project_id, test_env_id):
    res = TestEnv.find_one({'_id': ObjectId(test_env_id)})
    return jsonify({'status': 'ok', 'data': common.format_response_in_dic(res)}) if res else \
        jsonify({'status': 'failed', 'data': '未找到该env信息'})


@app.route('/api/project/<project_id>/addTestEnv', methods=['POST'])
@login_required
@roles_required('admin')
def add_test_env(project_id):
    try:
        request_data = request.get_json()
        request_data['status'] = True
        request_data['projectId'] = ObjectId(project_id)
        request_data['createAt'] = datetime.utcnow()
        filtered_data = TestEnv.filter_field(request_data, use_set_default=True)
        TestEnv.insert(filtered_data)
        return jsonify({'status': 'ok', 'data': '新建成功'})
    except BaseException as e:
        return jsonify({'status': 'failed', 'data': '新建失败 %s' % e})


@app.route('/api/project/<project_id>/updateTestEnv/<test_env_id>', methods=['POST'])
@login_required
@roles_required('admin')
def update_test_env(project_id, test_env_id):
    try:
        request_data = request.get_json()
        request_data['lastUpdateTime'] = datetime.utcnow()
        filtered_data = TestEnv.filter_field(request_data)
        update_response = TestEnv.update({'_id': ObjectId(test_env_id)}, {'$set': filtered_data})
        if update_response['n'] == 0:
            return jsonify({'status': 'failed', 'data': '未找到相应的更新数据！'})
        return jsonify({'status': 'ok', 'data': '更新成功'})
    except BaseException as e:
        return jsonify({'status': 'failed', 'data': '更新失败 %s' % e})


def get_env_name_and_domain(test_env_id):
    if test_env_id:
        test_env_info = common.format_response_in_dic(TestEnv.find_one({'_id': ObjectId(test_env_id), 'status': True}))
        return test_env_info['name'], test_env_info['domain']
    else:
        raise ValueError("test_env_id should not be empty")
