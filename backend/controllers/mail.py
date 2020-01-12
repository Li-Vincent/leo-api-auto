from datetime import datetime

from bson import ObjectId
from flask import jsonify, request
from flask_security import login_required, roles_accepted

from app import app
from models.mail import Mail
from utils import common


@app.route('/api/project/<project_id>/mailList', methods=['GET'])
@login_required
def mail_list(project_id):
    total_num, mails = common.get_total_num_and_arranged_data(Mail, request.args, fuzzy_fields=['name'])
    return jsonify({'status': 'ok', 'data': {'totalNum': total_num, 'rows': mails}})


@app.route('/api/project/<project_id>/addMail', methods=['POST'])
@login_required
@roles_accepted('admin', 'project')
def add_mail(project_id):
    try:
        request_data = request.get_json()
        request_data["status"] = True
        request_data["projectId"] = ObjectId(project_id)
        request_data["createAt"] = datetime.utcnow()
        filtered_data = Mail.filter_field(request.get_json(), use_set_default=True)
        Mail.insert(filtered_data)
        return jsonify({'status': 'ok', 'data': '新增邮件成功'})
    except BaseException as e:
        return jsonify({'status': 'failed', 'data': '新增邮件失败 %s' % e})


@app.route('/api/project/<project_id>/updateMail/<mail_id>', methods=['POST'])
@login_required
@roles_accepted('admin', 'project')
def update_mail(project_id, mail_id):
    try:
        request_data = request.get_json()
        request_data['lastUpdateTime'] = datetime.utcnow()
        filtered_data = Mail.filter_field(request_data)
        update_response = Mail.update({'_id': ObjectId(mail_id)}, {'$set': filtered_data})
        if update_response['n'] == 0:
            return jsonify({'status': 'failed', 'data': '未找到相应的更新数据！'})
        return jsonify({'status': 'ok', 'data': '更新成功'})
    except BaseException as e:
        return jsonify({'status': 'failed', 'data': '更新失败 %s' % e})
