import time

from flask import jsonify, request, current_app

from app import app
from utils.common import can_convert_to_int


@app.route('/api/function/waitFor', methods=['GET', 'POST'])
def wait_for():
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
