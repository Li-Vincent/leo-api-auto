from datetime import datetime

from flask import jsonify, request, abort, current_app
from flask_security import login_user, logout_user, login_required, roles_required, current_user
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import check_password_hash, generate_password_hash

from app import app, security, login_manager, user_data_store
from models.leo_user import LeoUser
from models.role import Role
from utils import common


# add favicon.ico
@app.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('favicon.ico')


def query_user(email):
    try:
        user = LeoUser.find_one({'email': email})
        return common.format_response_in_dic(user) if user else None
    except BaseException as e:
        with app.app_context():
            current_app.logger.error("query_user failed. - %s" % str(e))
        return None


def generate_auth_token(email, roles=['user'], expiration=7200):
    serializer = Serializer(app.config["SECRET_KEY"], expires_in=expiration)
    token = serializer.dumps({"email": email, "roles": roles})
    return token


@login_manager.unauthorized_handler
def unauthorized_handler():
    abort(401)


@security.unauthorized_handler
def unauthorized_handler():
    abort(403)


@app.route('/api/login', methods=['POST'])
def login():
    request_data = request.get_json()
    email = request_data.get('email') if request_data else None
    pass_word = request_data.get('password') if request_data else None
    user = user_data_store.find_user(email=email)
    if not user:
        return jsonify({'status': 'failed', 'data': '当前用户不存在！'})
    if not user.is_active:
        return jsonify({'status': 'failed', 'data': '当前用户被禁用，请联系管理员！'})
    if user is not None and check_password_hash(user.password, pass_word):
        login_user(user, remember=True)
        roles_name = []
        for role in user.roles:
            if role and role.name not in roles_name:
                roles_name.append(role.name)
        token = generate_auth_token(email, roles_name)
        current_app.logger.info("login successfully. email: %s" % str(email))
        return jsonify({'status': 'ok', 'data': {'email': email, 'token': token.decode("ascii")}})
    else:
        return jsonify({'status': 'failed', 'data': '用户名 / 密码错误！'})


@app.route('/api/register', methods=['POST'])
@login_required
@roles_required('admin')
def register():
    try:
        request_data = request.get_json()
        if query_user(request_data["email"]):
            return jsonify({'status': 'failed', 'data': '该邮箱已存在'})
        password_hash = generate_password_hash(request_data["password"])
        user_data_store.create_user(email=request_data['email'], password=password_hash, createAt=datetime.utcnow())
        user = user_data_store.find_user(email=request_data['email'])
        for role in request_data['roles']:
            user_data_store.add_role_to_user(user, role)
        current_app.logger.info("register user successfully. email: %s" % str(request_data['email']))
        return jsonify({'status': 'ok', 'data': '注册成功'})
    except BaseException as e:
        current_app.logger.error("register user failed. - %s" % str(e))
        return jsonify({'status': 'failed', 'data': 'register failed %s' % e})


@app.route('/api/logout', methods=['GET', 'POST'])
def logout():
    try:
        logout_user()
        return jsonify({'status': 'ok', 'data': '退出登录成功'})
    except BaseException as e:
        current_app.logger.error("logout user failed. - %s" % str(e))
        return jsonify({'status': 'failed', 'data': '退出登录失败! %s' % e})


@app.route('/api/user/<email>/role', methods=['GET'])
def get_user_roles(email):
    user = user_data_store.find_user(email=email)
    if user is not None:
        roles_name = []
        for role in user.roles:
            if role and role.name not in roles_name:
                roles_name.append(role.name)
        return jsonify({'status': 'ok', 'data': {'roles': roles_name}})
    else:
        return jsonify({'status': 'failed', 'data': '用户名 / 密码错误！'})


@app.route('/api/user/users', methods=['GET'])
@login_required
@roles_required('admin')
def get_user_list():
    total_num, users = common.get_total_num_and_arranged_data(LeoUser, request.args, fuzzy_fields=['email'])
    for user in users:
        user_data = user_data_store.find_user(email=user['email'])
        roles_name = []
        for role in user_data.roles:
            if role and role.name not in roles_name:
                roles_name.append(role.name)
        user['roleNames'] = roles_name
    return jsonify({'status': 'ok', 'data': {'totalNum': total_num, 'rows': users}})


@app.route('/api/user/roles', methods=['GET'])
@login_required
@roles_required('admin')
def get_role_list():
    total_num, roles = common.get_total_num_and_arranged_data(Role, request.args)
    return jsonify({'status': 'ok', 'data': {'totalNum': total_num, 'rows': roles}})


@app.route('/api/user/updateStatus', methods=['POST'])
@login_required
@roles_required('admin')
def update_user_status():
    try:
        data = request.get_json()
        user = user_data_store.find_user(email=data['email'])
        if data['active']:
            user_data_store.activate_user(user)
        else:
            user_data_store.deactivate_user(user)
        filtered_data = LeoUser.filter_field(data)
        update_response = LeoUser.update({'email': data['email']}, {'$set': filtered_data})
        if update_response['n'] == 0:
            return jsonify({'status': 'failed', 'data': '未找到相应的更新数据！'})
        return jsonify({'status': 'ok', 'data': '变更用户状态成功'})
    except BaseException as e:
        current_app.logger.error("update_user_status failed. - %s" % str(e))
        return jsonify({'status': 'failed', 'data': '变更用户状态失败! %s' % e})


@app.route('/api/user/changePassword', methods=['POST'])
@login_required
def change_password():
    try:
        data = request.get_json()
        login_email = current_user.email
        if data['email'] and data['email'] != login_email:
            return jsonify({'status': 'failed', 'data': '要修改的用户和登录用户不一致！'})
        if not check_password_hash(current_user.password, data['oldPassword']):
            return jsonify({'status': 'failed', 'data': '请输入正确的初始密码！'})
        data['password'] = generate_password_hash(data["password"])
        filtered_data = LeoUser.filter_field(data)
        update_response = LeoUser.update({'email': data['email']}, {'$set': filtered_data})
        if update_response['n'] == 0:
            return jsonify({'status': 'failed', 'data': '未找到要修改的用户！'})
        return jsonify({'status': 'ok', 'data': '修改密码成功,请重新登录'})
    except BaseException as e:
        current_app.logger.error("change_password failed. - %s" % str(e))
        return jsonify({'status': 'failed', 'data': '修改密码失败! %s' % e})


@app.route('/api/user/<email>/changeRoles', methods=['POST'])
@login_required
@roles_required('admin')
def change_roles(email):
    try:
        data = request.get_json()
        email = data['email'] if data['email'] else email
        user = user_data_store.find_user(email=email)
        if user is not None:
            # 先remove所有权限
            current_roles_name = []
            for role in user.roles:
                if role and role.name not in current_roles_name:
                    current_roles_name.append(role.name)
            for role in current_roles_name:
                user_data_store.remove_role_from_user(user, role)
            for role_name in data['roleNames']:
                user_data_store.add_role_to_user(user, role_name)
            return jsonify({'status': 'ok', 'data': '变更权限成功'})
        else:
            return jsonify({'status': 'failed', 'data': '未找到要修改的用户！'})
    except BaseException as e:
        current_app.logger.error("change_roles failed. - %s" % str(e))
        return jsonify({'status': 'failed', 'data': '变更权限失败! %s' % e})


@app.route('/api/user/<email>/resetPassword', methods=['POST'])
@login_required
@roles_required('admin')
def reset_password(email):
    try:
        data = request.get_json()
        email = data['email'] if data['email'] else email
        data['password'] = generate_password_hash(data["password"])
        filtered_data = LeoUser.filter_field(data)
        update_response = LeoUser.update({'email': email}, {'$set': filtered_data})
        if update_response['n'] == 0:
            return jsonify({'status': 'failed', 'data': '未找到要修改的用户！'})
        return jsonify({'status': 'ok', 'data': '重置密码成功: %s' % email})
    except BaseException as e:
        current_app.logger.error("reset_password failed. - %s" % str(e))
        return jsonify({'status': 'failed', 'data': '重置密码失败! %s' % e})


@app.route('/api/user/deleteUsers', methods=['POST'])
@login_required
@roles_required('admin')
def delete_users():
    try:
        data = request.get_json()
        if not data['users']:
            return jsonify({'status': 'failed', 'data': 'users为空'})
        else:
            users = data['users']
            print(users)
            delete_count = 0
            for email in users:
                res = LeoUser.delete_one({'email': email})
                delete_count += res.deleted_count
            return jsonify({'status': 'ok', 'data': '删除用户成功,删除数量: %s' % delete_count})
    except BaseException as e:
        current_app.logger.error("delete_users failed. - %s" % str(e))
        return jsonify({'status': 'failed', 'data': '删除用户失败! %s' % e})


@app.route('/api/user/<email>/changeProjects', methods=['POST'])
@login_required
@roles_required('admin')
def change_projects(email):
    try:
        data = request.get_json()
        if "userProjects" not in data:
            return jsonify({'status': 'failed', 'data': '请输入用户Projects！'})
        email = data['email'] if data['email'] else email
        user = user_data_store.find_user(email=email)
        if user is not None:
            filtered_data = LeoUser.filter_field(data)
            update_response = LeoUser.update({'email': email}, {'$set': filtered_data})
            if update_response['n'] == 0:
                return jsonify({'status': 'failed', 'data': '未找到要修改的用户！'})
            return jsonify({'status': 'ok', 'data': '变更用户项目成功: %s' % email})
        else:
            return jsonify({'status': 'failed', 'data': '未找到要修改的用户！'})
    except BaseException as e:
        current_app.logger.error("change_roles failed. - %s" % str(e))
        return jsonify({'status': 'failed', 'data': '变更用户项目失败! %s' % e})
