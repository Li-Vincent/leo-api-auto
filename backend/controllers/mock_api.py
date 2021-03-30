import time
from flask import request, jsonify, make_response

from app import app
from controllers.mock_data import request_method_list, get_mock_data


@app.route('/mock/<path:path>', methods=request_method_list)
def mock_call(path):
    try:
        if not path.startswith('/'):
            path = "/" + path
        method = request.method
        mock_data = get_mock_data(method, path)
        if mock_data:
            if 'delaySeconds' in mock_data and mock_data.get('delaySeconds') > 0:
                time.sleep(mock_data.get('delaySeconds'))
            return make_response(jsonify(mock_data.get('responseBody')), mock_data.get('responseCode'))
        else:
            return make_response(jsonify({
                'status': 'failed',
                'msg': 'MockData不存在'
            }), 400)
    except BaseException as e:
        return make_response(jsonify({"error": str(e)}), 500)
