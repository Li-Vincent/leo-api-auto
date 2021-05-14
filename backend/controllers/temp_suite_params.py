#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime

from bson import ObjectId
from flask import current_app, jsonify
from flask_security import login_required, current_user

from app import app
from models.temp_suite_params import TempSuiteParams

EMPIRES_TIME = 1800


# add by vincent.li for save suite params and get suite params for debug api cases.  --20200724

def get_temp_params_by_suite(test_suite_id):
    try:
        if not test_suite_id:
            current_app.logger.error("test suite id is required.")
            raise ValueError("test suite id is required.")
        res = TempSuiteParams.find_one({'testSuiteId': ObjectId(test_suite_id)})
        if res:
            now = datetime.datetime.utcnow()
            expires_time = res["expiresTime"]
            params = res["params"]
            if expires_time > now and isinstance(params, dict) and params:
                return params
            else:
                return {}
        else:
            return {}
    except BaseException as e:
        with app.app_context():
            current_app.logger.error("get temp params by suite failed. - %s" % str(e))
        return {}


@app.route('/api/getTestSuiteTempParams/<test_suite_id>', methods=['GET'])
@login_required
def get_suite_temp_params(test_suite_id):
    try:
        if not test_suite_id:
            raise ValueError("test suite id is required.")
        res = TempSuiteParams.find_one({'testSuiteId': ObjectId(test_suite_id)})
        if res and isinstance(res["params"], dict) and len(res["params"]) > 0:
            expires_time = res["expiresTime"]
            param_list = []
            for k, v in res["params"].items():
                param_list.append({"name": k, "value": v})
            return jsonify({'status': 'ok', 'data': {
                "expires_time": expires_time,
                "params": param_list
            }})
        else:
            return jsonify({'status': 'ok', 'data': {
                "params": None
            }})
    except BaseException as e:
        with app.app_context():
            current_app.logger.error("get temp params by suite failed. - %s" % str(e))
        return jsonify({'status': 'failed', 'data': "获取临时变量失败: " % str(e)})


def save_temp_params_for_suite(test_suite_id, params):
    try:
        if not test_suite_id or not params:
            current_app.logger.error("test suite id and params are required.")
            raise ValueError("test suite id is required.")
        now = datetime.datetime.utcnow()
        expires_time = now + datetime.timedelta(seconds=EMPIRES_TIME)
        res = TempSuiteParams.find_one({'testSuiteId': ObjectId(test_suite_id)})
        if res:
            update_data = dict()
            update_data['updateTime'] = now
            update_data['expiresTime'] = expires_time
            update_data['params'] = params
            update_data = TempSuiteParams.filter_field(update_data, use_set_default=True)
            update_response = TempSuiteParams.update({"testSuiteId": ObjectId(test_suite_id)},
                                                     {'$set': update_data})
            if update_response["n"] == 0:
                return {'status': 'failed', 'message': '未找到相应更新数据！'}
            return {'status': 'ok', 'message': '更新params成功！'}
        else:
            insert_data = dict()
            insert_data['updateTime'] = now
            insert_data['expiresTime'] = expires_time
            insert_data['params'] = params
            insert_data['testSuiteId'] = ObjectId(test_suite_id)
            insert_data = TempSuiteParams.filter_field(insert_data, use_set_default=True)
            TempSuiteParams.insert(insert_data)
            return {'status': 'ok', 'message': '新增temp suite params成功！'}
    except BaseException as e:
        with app.app_context():
            current_app.logger.error("get temp params by suite failed. - %s" % str(e))
        return {'status': 'failed', 'message': '新建/更新temp suite params失败 %s' % str(e)}
