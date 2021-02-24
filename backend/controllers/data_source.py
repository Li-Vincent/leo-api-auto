from datetime import datetime

from bson import ObjectId
from flask import jsonify, request, current_app
from flask_security import login_required, roles_required

from app import app
from models.data_source import DBConfig, DBEnvConnect
from utils import common


@app.route('/api/dbConfig/dbConfigList', methods=['GET'])
@login_required
def db_config_list():
    total_num, dbs = common.get_total_num_and_arranged_data(DBConfig, request.args)
    return jsonify({'status': 'ok', 'data': {'totalNum': total_num, 'rows': dbs}})


@app.route('/api/dbConfig/<db_config_id>', methods=['GET'])
@login_required
def get_db_config(db_config_id):
    try:
        res = DBConfig.find_one({'_id': ObjectId(db_config_id)})
        return jsonify({'status': 'ok', 'data': common.format_response_in_dic(res)}) if res else \
            jsonify({'status': 'failed', 'data': '未找到该dbConfig信息'})
    except BaseException as e:
        current_app.logger.error("get db config failed. - %s" % str(e))
        return jsonify({'status': 'failed', 'data': '出错了 %s' % e})


@app.route('/api/dbConfig/addDBConfig', methods=['POST'])
@login_required
@roles_required('admin')
def add_db_config():
    try:
        request_data = request.get_json()
        request_data['status'] = True
        request_data['createAt'] = datetime.utcnow()
        filtered_data = DBConfig.filter_field(request_data, use_set_default=True)
        DBConfig.insert(filtered_data)
        current_app.logger.info("add db config successfully. DB Config Name: %s" % str(filtered_data['name']))
        return jsonify({'status': 'ok', 'data': '新增DB配置成功'})
    except BaseException as e:
        current_app.logger.error("add db config failed. - %s" % str(e))
        return jsonify({'status': 'failed', 'data': '新建失败 %s' % e})


@app.route('/api/dbConfig/updateDBConfig/<db_config_id>', methods=['POST'])
@login_required
@roles_required('admin')
def update_db_config(db_config_id):
    try:
        request_data = request.get_json()
        request_data['lastUpdateTime'] = datetime.utcnow()
        filtered_data = DBConfig.filter_field(request_data)
        update_response = DBConfig.update({'_id': ObjectId(db_config_id)}, {'$set': filtered_data})
        if update_response['n'] == 0:
            return jsonify({'status': 'failed', 'data': '未找到相应的更新数据！'})
        current_app.logger.info("update db config successfully. DB Config ID: %s" % str(db_config_id))
        return jsonify({'status': 'ok', 'data': '更新DB配置成功'})
    except BaseException as e:
        current_app.logger.error("update db config failed. - %s" % str(e))
        return jsonify({'status': 'failed', 'data': '更新DB配置失败 %s' % e})


@app.route('/api/dbConfig/getDBEnvConnect', methods=['POST'])
@login_required
def get_db_env_connect():
    try:
        request_data = request.get_json()
        db_config_id = request_data['dbConfigId']
        test_env_id = request_data['testEnvId']
        if not db_config_id or not test_env_id:
            return jsonify({'status': 'failed', 'data': '参数不完整'})
        res = DBEnvConnect.find_one({'dbConfigId': ObjectId(db_config_id), 'testEnvId': ObjectId(test_env_id)})
        return jsonify({'status': 'ok', 'data': common.format_response_in_dic(res)}) if res else \
            jsonify({'status': 'ok', 'data': {'dbHost': ''}})
    except BaseException as e:
        current_app.logger.error("get db env connect failed. - %s" % str(e))
        return jsonify({'status': 'failed', 'data': '出错了 %s' % e})


@app.route('/api/dbConfig/updateDBEnvConnect', methods=['POST'])
@login_required
@roles_required('admin')
def update_db_env_connect():
    try:
        request_data = request.get_json()
        print(request_data)
        if not request_data['dbConfigId'] or not request_data['testEnvId']:
            return jsonify({'status': 'failed', 'data': '参数不完整,dbConfigId/testEnvId'})
        request_data['dbConfigId'] = ObjectId(request_data['dbConfigId'])
        request_data['testEnvId'] = ObjectId(request_data['testEnvId'])
        db_config_id = request_data['dbConfigId']
        test_env_id = request_data['testEnvId']
        res = DBEnvConnect.find_one({'dbConfigId': ObjectId(db_config_id), 'testEnvId': ObjectId(test_env_id)})

        if res:
            request_data['lastUpdateTime'] = datetime.utcnow()
            filtered_data = DBEnvConnect.filter_field(request_data, use_set_default=True)
            update_response = DBEnvConnect.update(
                {'dbConfigId': ObjectId(db_config_id), 'testEnvId': ObjectId(test_env_id)}, {'$set': filtered_data})
            if update_response['n'] == 0:
                return jsonify({'status': 'failed', 'data': '未找到相应的更新数据！'})
            return jsonify({'status': 'ok', 'data': '更新DB连接配置成功'})
        else:
            request_data['createAt'] = datetime.utcnow()
            request_data['createUser'] = request_data['lastUpdateUser']
            request_data['lastUpdateTime'] = datetime.utcnow()
            filtered_data = DBEnvConnect.filter_field(request_data, use_set_default=True)
            DBEnvConnect.insert(filtered_data)
        return jsonify({'status': 'ok', 'data': '更新DB连接配置成功'})
    except BaseException as e:
        current_app.logger.error("update db env connect failed. - %s" % str(e))
        return jsonify({'status': 'failed', 'data': '变更DB连接配置失败 %s' % e})


def get_db_connect(db_config_id, test_env_id):
    try:
        if not db_config_id or not test_env_id:
            return jsonify({'status': 'failed', 'data': '参数不完整'})
        res = DBEnvConnect.find_one({'dbConfigId': ObjectId(db_config_id), 'testEnvId': ObjectId(test_env_id)})
        return common.format_response_in_dic(res) if res else None
    except BaseException as e:
        with app.app_context():
            current_app.logger.error("get db connect failed. - %s" % str(e))
        return None
