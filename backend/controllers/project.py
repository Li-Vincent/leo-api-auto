from datetime import datetime

from bson import ObjectId
from flask import jsonify, request
from flask_security import login_required

from app_init import app
from models.project import Project
from utils import common


@app.route('/api/project/projectList', methods=['GET'])
@login_required
def project_list():
    total_num, projects = common.get_total_num_and_arranged_data(Project, request.args, fuzzy_fields=['name'])
    return jsonify({'status': 'ok', 'data': {'totalNum': total_num, 'rows': projects}})


@app.route('/api/project/<project_id>', methods=['GET'])
@login_required
def get_project(project_id):
    res = Project.find_one({'_id': ObjectId(project_id)})
    return jsonify({'status': 'ok', 'data': common.format_response_in_dic(res)})


@app.route('/api/project/addProject', methods=['POST'])
@login_required
def add_project():
    try:
        params = request.get_json()
        params['createAt'] = datetime.utcnow()
        filtered_data = Project.filter_field(params, use_set_default=True)
        Project.insert(filtered_data)
        return jsonify({'status': 'ok', 'data': '新建成功'})
    except BaseException as e:
        return jsonify({'status': 'failed', 'data': '新建失败 %s' % e})


@app.route('/api/project/<project_id>/updateProject', methods=['POST'])
@login_required
def update_project(project_id):
    try:
        filtered_data = Project.filter_field(request.get_json())
        for key, value in filtered_data.items():
            Project.update({"_id": ObjectId(project_id)},
                           {'$set': {key: value}})
        update_response = Project.update({"_id": ObjectId(project_id)},
                                         {'$set': {'lastUpdateTime': datetime.utcnow()}}, )
        if update_response["n"] == 0:
            return jsonify({'status': 'failed', 'data': '未找到相应更新数据！'})
        return jsonify({'status': 'ok', 'data': '更新成功'})
    except BaseException as e:
        return jsonify({'status': 'failed', 'data': '更新失败: %s' % e})


@app.route('/favicon.ico')
def get_fav():
    return app.send_static_file('favicon.ico')
