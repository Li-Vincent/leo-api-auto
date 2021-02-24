from datetime import datetime

import pymongo
from bson import ObjectId
from flask import jsonify, request, current_app
from flask_security import login_required, roles_required

from app import app
from models.mail import MailSender
from utils import common
from utils.send_email import send_email


@app.route('/api/mailConfig/mailSenderList', methods=['GET'])
@login_required
def mail_sender_list():
    total_num, mail_senders = common.get_total_num_and_arranged_data(MailSender, request.args)
    return jsonify({'status': 'ok', 'data': {'totalNum': total_num, 'rows': mail_senders}})


@app.route('/api/mailConfig/addMailSender', methods=['POST'])
@login_required
@roles_required('admin')
def add_mail_sender():
    try:
        request_data = request.get_json()
        request_data["status"] = True
        request_data["createAt"] = datetime.utcnow()
        filtered_data = MailSender.filter_field(request.get_json(), use_set_default=True)
        MailSender.insert(filtered_data)
        return jsonify({'status': 'ok', 'data': '新增邮件发件人成功'})
    except BaseException as e:
        current_app.logger.error("add_mail_sender failed. - %s" % str(e))
        return jsonify({'status': 'failed', 'data': '新增邮件发件人失败 %s' % e})


@app.route('/api/mailConfig/updateMailSender/<sender_id>', methods=['POST'])
@login_required
@roles_required('admin')
def update_mail_sender(sender_id):
    try:
        request_data = request.get_json()
        request_data['lastUpdateTime'] = datetime.utcnow()
        filtered_data = MailSender.filter_field(request_data)
        update_response = MailSender.update({'_id': ObjectId(sender_id)}, {'$set': filtered_data})
        if update_response['n'] == 0:
            return jsonify({'status': 'failed', 'data': '未找到相应的更新数据！'})
        return jsonify({'status': 'ok', 'data': '更新发件人成功'})
    except BaseException as e:
        current_app.logger.error("update_mail_sender failed. - %s" % str(e))
        return jsonify({'status': 'failed', 'data': '更新发件人失败 %s' % e})


@app.route('/api/mailConfig/mailSenderTest', methods=['POST'])
@login_required
@roles_required('admin')
def test_email_sender():
    request_data = request.get_json()
    from_email = request_data.get('email')
    password = request_data.get('password')
    smtp_server = request_data.get('SMTPServer')
    smtp_port = request_data.get('SMTPPort')
    status, msg = send_email(smtp_server, smtp_port, from_email, password, [from_email], '发件人测试title',
                             'mail sender content')
    if status:
        return jsonify({'status': 'ok', 'data': '验证通过 (*^▽^*) 您可以放心「提交」了'})
    else:
        return jsonify({'status': 'failed', 'data': '验证失败 o(╥﹏╥)o', 'message': msg})


def send_cron_email(to_list, subject, content):
    try:
        mail_sender = list(MailSender.find({}).sort([('createAt', pymongo.DESCENDING)]).limit(1))[0]
        from_email = mail_sender.get('email')
        password = mail_sender.get('password')
        smtp_server = mail_sender.get('SMTPServer')
        smtp_port = mail_sender.get('SMTPPort')
        status, msg = send_email(smtp_server, smtp_port, from_email, password, to_list, subject, content)
        if status:
            return {'status': 'ok', 'data': '邮件发送成功'}
        else:
            with app.app_context():
                current_app.logger.error("send_cron_mail failed. - %s" % str(msg))
            return {'status': 'failed', 'data': '邮件发送失败', 'message': msg}
    except BaseException as e:
        with app.app_context():
            current_app.logger.error("send_cron_mail failed. - %s" % str(e))
        return {'status': 'failed', 'data': '邮件发送失败', 'error': str(e)}
