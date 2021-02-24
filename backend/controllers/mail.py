from datetime import datetime

from bson import ObjectId
from flask import jsonify, request, current_app
from flask_security import login_required, roles_accepted

from app import app
from models.mail import MailRecipient, MailGroup
from utils import common


@app.route('/api/mailConfig/mailList', methods=['GET'])
@login_required
def mail_list():
    total_num, mails = common.get_total_num_and_arranged_data(MailRecipient, request.args, fuzzy_fields=['email'])
    return jsonify({'status': 'ok', 'data': {'totalNum': total_num, 'rows': mails}})


@app.route('/api/mailConfig/mailGroupList', methods=['GET'])
@login_required
def mail_group_list():
    total_num, mail_groups = common.get_total_num_and_arranged_data(MailGroup, request.args, fuzzy_fields=['name'])
    return jsonify({'status': 'ok', 'data': {'totalNum': total_num, 'rows': mail_groups}})


@app.route('/api/mailConfig/addMail', methods=['POST'])
@login_required
@roles_accepted('admin', 'project')
def add_mail():
    try:
        request_data = request.get_json()
        request_data["status"] = True
        if request_data["mailGroupId"]:
            request_data["mailGroupId"] = ObjectId(request_data["mailGroupId"])
        request_data["createAt"] = datetime.utcnow()
        filtered_data = MailRecipient.filter_field(request.get_json(), use_set_default=True)
        MailRecipient.insert(filtered_data)
        return jsonify({'status': 'ok', 'data': '新增收件人成功'})
    except BaseException as e:
        current_app.logger.error("add_mail failed. - %s" % str(e))
        return jsonify({'status': 'failed', 'data': '新增收件人失败 %s' % e})


@app.route('/api/mailConfig/addMailGroup', methods=['POST'])
@login_required
@roles_accepted('admin')
def add_mail_group():
    try:
        request_data = request.get_json()
        request_data["status"] = True
        request_data["createAt"] = datetime.utcnow()
        filtered_data = MailGroup.filter_field(request.get_json(), use_set_default=True)
        MailGroup.insert(filtered_data)
        return jsonify({'status': 'ok', 'data': '新增邮件分组成功'})
    except BaseException as e:
        current_app.logger.error("add_mail failed. - %s" % str(e))
        return jsonify({'status': 'failed', 'data': '新增邮件分组失败 %s' % e})


@app.route('/api/mailConfig/updateMail/<mail_id>', methods=['POST'])
@login_required
@roles_accepted('admin', 'project')
def update_mail(mail_id):
    try:
        request_data = request.get_json()
        request_data['lastUpdateTime'] = datetime.utcnow()
        if 'mailGroupId' in request_data and request_data["mailGroupId"]:
            request_data["mailGroupId"] = ObjectId(request_data["mailGroupId"])
        filtered_data = MailRecipient.filter_field(request_data)
        update_response = MailRecipient.update({'_id': ObjectId(mail_id)}, {'$set': filtered_data})
        if update_response['n'] == 0:
            return jsonify({'status': 'failed', 'data': '未找到相应的更新数据！'})
        return jsonify({'status': 'ok', 'data': '更新成功'})
    except BaseException as e:
        current_app.logger.error("update_mail failed. - %s" % str(e))
        return jsonify({'status': 'failed', 'data': '更新失败 %s' % e})


@app.route('/api/mailConfig/updateMailGroup/<mail_group_id>', methods=['POST'])
@login_required
@roles_accepted('admin')
def update_mail_group(mail_group_id):
    try:
        request_data = request.get_json()
        request_data['lastUpdateTime'] = datetime.utcnow()
        filtered_data = MailGroup.filter_field(request_data)
        update_response = MailGroup.update({'_id': ObjectId(mail_group_id)}, {'$set': filtered_data})
        if update_response['n'] == 0:
            return jsonify({'status': 'failed', 'data': '未找到相应的更新数据！'})
        return jsonify({'status': 'ok', 'data': '更新成功'})
    except BaseException as e:
        current_app.logger.error("update_mail failed. - %s" % str(e))
        return jsonify({'status': 'failed', 'data': '更新失败 %s' % e})


def get_mails_by_group(mail_group_id_list):
    try:
        returned_mail_list = []
        if not mail_group_id_list or not isinstance(mail_group_id_list, list):
            raise TypeError('mail group id list参数不正确')
        active_mail_group_id_list = []
        for mail_group_id in mail_group_id_list:
            result = MailGroup.find_one({'_id': ObjectId(mail_group_id), 'status': True})
            if result:
                active_mail_group_id_list.append(common.format_response_in_dic(result).get('_id'))
        for mail_group_id in active_mail_group_id_list:
            cursor = MailRecipient.find({'mailGroupId': ObjectId(mail_group_id), 'status': True})
            for item in cursor:
                returned_mail_list.append(common.format_response_in_dic(item).get('email'))
        returned_mail_list = list(set(returned_mail_list))
        return returned_mail_list if returned_mail_list else None
    except BaseException as e:
        with app.app_context():
            current_app.logger.error("get mail list failed. - %s" % str(e))
        return None
