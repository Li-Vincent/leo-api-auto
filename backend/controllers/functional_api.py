import time
import datetime

from flask import jsonify, request, current_app

from app import app
from utils.common import can_convert_to_int
from controllers.mail import get_mails_by_group


@app.route('/api/function/waitFor', methods=['GET', 'POST'])
def wait_for():
    # 等待seconds秒
    try:
        if request.method == 'POST':
            data = request.json
        elif request.method == 'GET':
            data = request.args
        if data.get("seconds") and can_convert_to_int(data.get("seconds")):
            time.sleep(int(data.get('seconds')))
            return jsonify({'status': 'ok', 'data': {'waitFor': data.get("seconds")}})
        else:
            return jsonify({'status': 'failed', 'data': {'error': "required param: seconds. type: int"}})
    except BaseException as e:
        current_app.logger.error("wait For failed. - %s" % str(e))
        return jsonify({'status': 'failed', 'data': 'wait For failed. - %s' % e})


@app.route('/api/function/getTimestamp', methods=['GET'])
def get_timestamp():
    # 获取当前时间戳，13位
    datetime_object = datetime.datetime.utcnow()
    now_timetuple = datetime_object.timetuple()
    now_second = time.mktime(now_timetuple)
    now_millisecond = int(now_second * 1000 + datetime_object.microsecond / 1000)
    return jsonify({'timestamp': now_millisecond})


