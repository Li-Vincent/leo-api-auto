import json
from datetime import datetime

from bson import ObjectId
from flask import jsonify, request, current_app
from flask_security import login_required, roles_accepted, current_user

from app import app
from models.mock_data import MockData
from utils import common

request_method_list = [
    'GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS'
]


@app.route('/api/mock/mockAPIList', methods=['GET'])
@login_required
def mock_api_list():
    total_num, mock_apis = common.get_total_num_and_arranged_data(MockData, request.args,
                                                                  fuzzy_fields=['name', 'category'])
    return jsonify({'status': 'ok', 'data': {'totalNum': total_num, 'rows': mock_apis}})


@app.route('/api/mock/mockAPI/<mock_api_id>', methods=['GET', 'POST'])
@login_required
def get_mock_api(mock_api_id):
    res = MockData.find_one({'_id': ObjectId(mock_api_id)})
    mock_api = common.format_response_in_dic(res)
    return jsonify({'status': 'ok', 'data': mock_api}) if mock_api else jsonify({'status': 'failed', 'data': None})


@app.route('/api/mock/addMockAPI', methods=['POST'])
@roles_accepted('admin', 'project')
def add_mock_api():
    try:
        request_data = request.get_json()
        if 'requestMethod' not in request_data:
            raise ValueError('please set requestMethod!')
        if request_data['requestMethod'] not in request_method_list:
            raise ValueError('requestMethod should in {}'.str(request_method_list))
        if 'path' not in request_data:
            raise ValueError('please set path!')
        if 'responseCode' not in request_data:
            raise ValueError('please set responseCode!')
        if 'responseBody' not in request_data:
            raise ValueError('please set responseBody!')
        request_data['responseBody'] = request_data['responseBody'].replace('\'', '\"')
        request_data['responseBody'] = json.loads(request_data['responseBody'])
        if not isinstance(request_data['responseBody'], dict):
            raise TypeError('responseBody should be a json!')
        request_data['delaySeconds'] = float(request_data['delaySeconds'])
        request_data["status"] = False
        request_data["isDeleted"] = False
        request_data["createAt"] = datetime.utcnow()
        request_data["createUser"] = current_user.email
        filtered_data = MockData.filter_field(request_data, use_set_default=True)
        res = MockData.find_one(
            {'path': filtered_data['path'], 'requestMethod': filtered_data['requestMethod'], 'isDeleted': False})
        if res:
            return jsonify({'status': 'failed', 'data': '存在相同Path+requestMethod的MockAPI, 不能重复添加'})
        MockData.insert(filtered_data)
        current_app.logger.info(
            "add mock api successfully. Name:{}, User:{}".format(filtered_data['name'], current_user.email))
        return jsonify({'status': 'ok', 'data': '添加MockAPI成功'})
    except BaseException as e:
        current_app.logger.error("add mock api failed. User:{}, Error:{}".format(current_user.email, str(e)))
        return jsonify({'status': 'failed', 'data': '添加MockAPI失败 %s' % str(e)})


@app.route('/api/mock/updateMockAPI/<mock_api_id>', methods=['POST'])
@roles_accepted('admin', 'project')
def update_mock_api(mock_api_id):
    try:
        request_data = request.get_json()
        res = MockData.find_one({'_id': ObjectId(mock_api_id)})
        if not res:
            return jsonify({'status': 'failed', 'data': '未找到要更新的MockAPI!'})
        update_data = common.format_response_in_dic(res)
        if 'requestMethod' in request_data:
            if request_data['requestMethod'] not in request_method_list:
                raise ValueError('requestMethod should in {}'.str(request_method_list))
        if 'responseBody' in request_data:
            request_data['responseBody'] = request_data['responseBody'].replace('\'', '\"')
            request_data['responseBody'] = json.loads(request_data['responseBody'])
            if not isinstance(request_data['responseBody'], dict):
                raise TypeError('responseBody should be a json!')
        if 'delaySeconds' in request_data:
            request_data['delaySeconds'] = float(request_data['delaySeconds'])
        update_data.update(request_data)
        update_data["lastUpdateTime"] = datetime.utcnow()
        update_data["lastUpdateUser"] = current_user.email
        update_data.pop('_id')
        update_data.pop('createAt')
        update_data.pop('createUser')
        filtered_data = MockData.filter_field(update_data, use_set_default=True)
        repeat_res = MockData.find_one({'_id': {'$ne': ObjectId(mock_api_id)},
                                        'path': filtered_data['path'],
                                        'requestMethod': filtered_data['requestMethod'],
                                        'isDeleted': False})
        if repeat_res:
            return jsonify({'status': 'failed', 'data': '存在相同Path+requestMethod的MockAPI, 不能更新'})
        update_response = MockData.update({'_id': ObjectId(mock_api_id)}, {'$set': filtered_data})
        if update_response["n"] == 0:
            return jsonify({'status': 'failed', 'data': '未找到要更新的MockAPI！'})
        current_app.logger.info("update mock api successfully. ID:{}, User:{}".format(mock_api_id, current_user.email))
        return jsonify({'status': 'ok', 'data': '更新MockAPI成功'})
    except BaseException as e:
        current_app.logger.error(
            "update mock api failed. ID:{},  User:{}, Error:{}".format(mock_api_id, current_user.email, str(e)))
        return jsonify({'status': 'failed', 'data': '更新MockAPI失败 %s' % str(e)})


def get_mock_data(method, path):
    try:
        if method not in request_method_list:
            raise ValueError("method should in {}".format(str(request_method_list)))
        res = MockData.find_one({
            'requestMethod': method,
            'path': path,
            'status': True,
            'isDeleted': False
        })
        mock_data = None
        if res:
            mock_data = common.format_response_in_dic(res)
        if mock_data and 'responseBody' in mock_data and 'responseCode' in mock_data:
            return mock_data
        else:
            return None
    except BaseException as e:
        with app.app_context():
            current_app.logger.error(
                "get mock data failed. method:{},  path:{}, Error:{}".format(method, path, str(e)))
        return None
