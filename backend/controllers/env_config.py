from datetime import datetime

from bson import ObjectId
from flask import jsonify, request, current_app
from flask_security import login_required, roles_required, current_user

from app import app
from models.env_config import EnvConfig
from utils import common


@app.route('/api/envConfig/envConfigList', methods=['GET'])
@login_required
def env_config_list():
    total_num, envs = common.get_total_num_and_arranged_data(EnvConfig, request.args, fuzzy_fields=['name'])
    return jsonify({'status': 'ok', 'data': {'totalNum': total_num, 'rows': envs}})


@app.route('/api/envConfig/<test_env_id>', methods=['GET'])
@login_required
def get_env_config(test_env_id):
    res = EnvConfig.find_one({'_id': ObjectId(test_env_id)})
    return jsonify({'status': 'ok', 'data': common.format_response_in_dic(res)}) if res else \
        jsonify({'status': 'failed', 'data': '未找到该envConfig信息'})


@app.route('/api/envConfig/addEnvConfig', methods=['POST'])
@login_required
@roles_required('admin')
def add_env_config():
    try:
        request_data = request.get_json()
        request_data['status'] = True
        request_data['createAt'] = datetime.utcnow()
        filtered_data = EnvConfig.filter_field(request_data, use_set_default=True)
        EnvConfig.insert(filtered_data)
        current_app.logger.info(
            "add env config successfully. ENV:{}, User:{}".format(str(filtered_data['name']), current_user.email))
        return jsonify({'status': 'ok', 'data': '新建成功'})
    except BaseException as e:
        current_app.logger.error("add env config failed. User:{}, Error:{}".format(current_user.email, str(e)))
        return jsonify({'status': 'failed', 'data': '新建失败 %s' % e})


@app.route('/api/envConfig/updateEnvConfig/<test_env_id>', methods=['POST'])
@login_required
@roles_required('admin')
def update_env_config(test_env_id):
    try:
        request_data = request.get_json()
        request_data['lastUpdateTime'] = datetime.utcnow()
        filtered_data = EnvConfig.filter_field(request_data)
        update_response = EnvConfig.update({'_id': ObjectId(test_env_id)}, {'$set': filtered_data})
        if update_response['n'] == 0:
            return jsonify({'status': 'failed', 'data': '未找到相应的更新数据！'})
        current_app.logger.info(
            "update env config successfully. ENV ID:{}, User:{}".format(str(test_env_id), current_user.email))
        return jsonify({'status': 'ok', 'data': '更新成功'})
    except BaseException as e:
        current_app.logger.error("update_env_config failed. User:{}, Error:{}".format(current_user.email, str(e)))
        return jsonify({'status': 'failed', 'data': '更新失败 %s' % e})


def get_env_name_and_domain(test_env_id):
    try:
        test_env_info = common.format_response_in_dic(
            EnvConfig.find_one({'_id': ObjectId(test_env_id), 'status': True}))
        if not test_env_info['protocol']:
            raise ValueError('测试环境protocol为空，请设置')
        if not test_env_info['domain']:
            raise ValueError('未找到任何「启用的」环境信息')
        if not test_env_info['name']:
            raise ValueError('测试环境名称为空，请设置环境名称')
        return test_env_info['name'], test_env_info['protocol'], test_env_info['domain']
    except BaseException as e:
        with app.context():
            current_app.logger.error("get_env_name_and_domain failed. %s" % str(e))
