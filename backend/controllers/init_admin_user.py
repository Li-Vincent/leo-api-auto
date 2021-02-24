from datetime import datetime

from bson import ObjectId
from flask import jsonify, request, current_app
from werkzeug.security import generate_password_hash

from app import app, user_data_store
from models.leo_user import LeoUser
from models.role import Role
from utils import common


def create_roles():
    user_data_store.find_or_create_role(name='admin', description='超级管理员')
    user_data_store.find_or_create_role(name='project', description='项目管理员')
    user_data_store.find_or_create_role(name='user', description='普通用户')


@app.route('/api/checkAdminUserExist', methods=['POST'])
def check_admin_user_exist():
    try:
        role = Role.find_one({'name': 'admin'})
        admin_role_id = common.format_response_in_dic(role)['_id'] if role else None
        admin_user = LeoUser.find_one({'roles': ObjectId(admin_role_id), 'active': True})
        admin_email = admin_user['email'] if admin_user else None
        return jsonify({'status': True, 'data': admin_email}) if admin_user and admin_email else jsonify(
            {'status': False})
    except BaseException as e:
        current_app.logger.error("check_admin_user_exist failed. - %s" % str(e))
        return jsonify({'status': False, 'data': "出错了，请刷新重试 ~ %s" % e})


def admin_user_existed():
    try:
        role = Role.find_one({'name': 'admin'})
        admin_role_id = common.format_response_in_dic(role)['_id'] if role else None
        admin_user = LeoUser.find_one({'roles': ObjectId(admin_role_id), 'active': True})
        admin_email = admin_user['email'] if admin_user else None
        return (True, admin_email) if admin_user and admin_email else (False, None)
    except BaseException as e:
        with app.app_context():
            current_app.logger.error("admin_user_existed failed. - %s" % str(e))
        return False, None


@app.route('/api/addAdminUser', methods=['POST'])
def add_admin_user():
    try:
        (existed, data) = admin_user_existed()
        if existed:
            return jsonify({'status': 'ok', data: '"管理员用户已经存在, 邮箱为 %s' % data})
        create_roles()
        request_data = request.get_json()
        email = request_data['email']
        password = request_data['password']
        roles = ['admin', 'user', 'project']
        password_hash = generate_password_hash(password)
        user_data_store.create_user(email=email, password=password_hash, createAt=datetime.utcnow())
        user = user_data_store.find_user(email=email)
        for role in roles:
            user_data_store.add_role_to_user(user, role)
        current_app.logger.info("add admin user successfully. email: %s" % str(email))
        return jsonify({'status': 'ok', 'data': '添加管理员用户成功'})
    except BaseException as e:
        current_app.logger.error("add admin user failed. - %s" % str(e))
        return jsonify({'status': 'failed', 'data': "出错了, Error: %s" % e})


if __name__ == '__main__':
    pass
