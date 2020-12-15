from datetime import datetime

from bson import ObjectId
from flask import jsonify, request, current_app
from flask_security import login_required, roles_accepted

from app import app
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
@roles_accepted('admin', 'project')
def add_project():
    try:
        params = request.get_json()
        params['createAt'] = datetime.utcnow()
        filtered_data = Project.filter_field(params, use_set_default=True)
        Project.insert(filtered_data)
        current_app.logger.info("add project successfully. Project: %s" % str(filtered_data['name']))
        return jsonify({'status': 'ok', 'data': '新建成功'})
    except BaseException as e:
        current_app.logger.error("add project failed. - %s" % str(e))
        return jsonify({'status': 'failed', 'data': '新建失败 %s' % e})


@app.route('/api/project/<project_id>/updateProject', methods=['POST'])
@login_required
@roles_accepted('admin', 'project')
def update_project(project_id):
    try:
        request_data = request.get_json()
        request_data['lastUpdateTime'] = datetime.utcnow()
        filtered_data = Project.filter_field(request_data)
        update_response = Project.update({'_id': ObjectId(project_id)}, {'$set': filtered_data})
        if update_response["n"] == 0:
            return jsonify({'status': 'failed', 'data': '未找到相应更新数据！'})
        current_app.logger.info("update project successfully. Project: %s" % str(project_id))
        return jsonify({'status': 'ok', 'data': '更新成功'})
    except BaseException as e:
        current_app.logger.error("update project failed. - %s" % str(e))
        return jsonify({'status': 'failed', 'data': '更新失败: %s' % e})
