from datetime import datetime

from bson import ObjectId
from werkzeug.security import generate_password_hash

from app_init import user_data_store
from models.leo_user import LeoUser
from models.role import Role
from utils import common


def create_roles():
    user_data_store.find_or_create_role(name='admin', description='超级管理员')
    user_data_store.find_or_create_role(name='project', description='项目管理员')
    user_data_store.find_or_create_role(name='user', description='普通用户')


def check_admin_user_exist():
    try:
        role = Role.find_one({'name': 'admin'})
        admin_role_id = common.format_response_in_dic(role)['_id'] if role else None
        admin_user = LeoUser.find_one({'roles': ObjectId(admin_role_id), 'active': True})
        admin_email = admin_user['email'] if admin_user else None
        return (True, admin_email) if admin_user and admin_email else (False, None)
    except BaseException as e:
        print(e)
        return False, e


def add_admin_user():
    try:
        (existed, data) = check_admin_user_exist()
        if existed:
            print("管理员用户已经存在, 邮箱为 {}".format(data))
            return
        elif data:
            print("出错了, %s " % data)
        email = input("Please input admin user email:\n")
        password = input("Please input password:\n")
        roles = ['admin', 'user', 'project']
        password_hash = generate_password_hash(password)
        user_data_store.create_user(email=email, password=password_hash, createAt=datetime.utcnow())
        user = user_data_store.find_user(email=email)
        for role in roles:
            user_data_store.add_role_to_user(user, role)
        print("添加管理员用户成功")
    except BaseException as e:
        print("出错了, Error: %s" % e)


if __name__ == '__main__':
    create_roles()
    add_admin_user()
