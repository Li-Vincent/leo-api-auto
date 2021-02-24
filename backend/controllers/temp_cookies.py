import datetime

from bson import ObjectId
from flask import current_app

from app import app
from models.temp_cookies import Cookies

EMPIRES_TIME = 1800


# add by vincent.li for save cookies and get cookies for debug api cases.  --20200705

def get_cookies_by_suite(test_suite_id):
    try:
        if not test_suite_id:
            current_app.logger.error("test suite id is required.")
            raise ValueError("test suite id is required.")
        res = Cookies.find_one({'testSuiteId': ObjectId(test_suite_id)})
        if res:
            now = datetime.datetime.utcnow()
            expires_time = res["expiresTime"]
            cookies = res["cookies"]
            return cookies if expires_time > now and len(cookies) else None
        else:
            return None
    except BaseException as e:
        with app.app_context():
            current_app.logger.error("get cookies by suite failed. - %s" % str(e))
        return None


def save_cookies_for_suite(test_suite_id, cookies):
    try:
        if not test_suite_id or not cookies:
            current_app.logger.error("test suite id and cookies are required.")
            raise ValueError("test suite id is required.")
        now = datetime.datetime.utcnow()
        expires_time = now + datetime.timedelta(seconds=EMPIRES_TIME)
        res = Cookies.find_one({'testSuiteId': ObjectId(test_suite_id)})
        if res:
            update_data = dict()
            update_data['updateTime'] = now
            update_data['expiresTime'] = expires_time
            update_data['cookies'] = cookies
            update_data = Cookies.filter_field(update_data, use_set_default=True)
            update_response = Cookies.update({"testSuiteId": ObjectId(test_suite_id)},
                                             {'$set': update_data})
            if update_response["n"] == 0:
                return {'status': 'failed', 'message': '未找到相应更新数据！'}
            return {'status': 'ok', 'message': '更新cookies成功！'}
        else:
            insert_data = dict()
            insert_data['updateTime'] = now
            insert_data['expiresTime'] = expires_time
            insert_data['cookies'] = cookies
            insert_data['testSuiteId'] = ObjectId(test_suite_id)
            insert_data = Cookies.filter_field(insert_data, use_set_default=True)
            Cookies.insert(insert_data)
            return {'status': 'ok', 'message': '新增cookies成功！'}
    except BaseException as e:
        with app.app_context():
            current_app.logger.error("get cookies by suite failed. - %s" % str(e))
        return {'status': 'failed', 'message': '新建/更新cookies失败 %s' % str(e)}
