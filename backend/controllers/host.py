from datetime import datetime

from bson import ObjectId
from flask import jsonify, request
from flask_security import login_required

from app_init import app
from models.host import Host
from utils import common


# 已弃用

@app.route('/api/project/<project_id>/hostList', methods=['GET'])
@login_required
def host_list(project_id):
    total_num, hosts = common.get_total_num_and_arranged_data(Host, request.args, fuzzy_fields=['name'])
    return jsonify({'status': 'ok', 'data': {'totalNum': total_num, 'rows': hosts}})


@app.route('/api/project/<project_id>/addHost', methods=['POST'])
@login_required
def add_host(project_id):
    try:
        request_data = request.get_json()
        request_data['status'] = True
        request_data['projectId'] = ObjectId(project_id)
        request_data['createAt'] = datetime.utcnow()
        filtered_data = Host.filter_field(request_data, use_set_default=True)
        Host.insert(filtered_data)
        return jsonify({'status': 'ok', 'data': '新建成功'})
    except BaseException as e:
        return jsonify({'status': 'failed', 'data': '新建失败 %s' % e})


@app.route('/api/project/<project_id>/updateHost/<host_id>', methods=['POST'])
@login_required
def update_host(project_id, host_id):
    try:
        request_data = request.get_json()
        request_data['lastUpdateTime'] = datetime.utcnow()
        filtered_data = Host.filter_field(request_data)
        update_response = Host.update({'_id': ObjectId(host_id)}, {'$set': filtered_data})
        if update_response['n'] == 0:
            return jsonify({'status': 'failed', 'data': '未找到相应的更新数据！'})
        return jsonify({'status': 'ok', 'data': '更新成功'})
    except BaseException as e:
        return jsonify({'status': 'failed', 'data': '更新失败 %s' % e})
