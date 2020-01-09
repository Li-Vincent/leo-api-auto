import sys
from datetime import timedelta

sys.path.append('..')
from flask import Flask, render_template
from flask_login import LoginManager
from flask_security import Security, MongoEngineUserDatastore, UserMixin, RoleMixin
from flask_mongoengine import MongoEngine
from flask_cors import CORS
from utils.db.mongo_orm import *

from config import Config

app = Flask(__name__, static_folder='../../dist/static', template_folder='../../dist')

_config = Config()

app.config['SECRET_KEY'] = _config.get_secret_key()
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # 设置session的保存时间=7days
# 解决中文乱码问题
app.config['JSON_AS_ASCII'] = False
# 禁止jsonify 按照key 自动排序
app.config['JSON_SORT_KEYS'] = False
login_manager = LoginManager()
login_manager.init_app(app)

cors = CORS(app, supports_credentials=True)

conn, db = connect(_config.get_mongo_db_name(),
                   ip=_config.get_mongo_host(),
                   port=int(_config.get_mongo_port()),
                   username=_config.get_mongo_username(),
                   password=_config.get_mongo_password())

# Create User database connection object
app.config['MONGODB_DB'] = _config.get_mongo_db_name()
app.config['MONGODB_HOST'] = _config.get_mongo_host()
app.config['MONGODB_PORT'] = int(_config.get_mongo_port())
app.config['MONGODB_USERNAME'] = _config.get_mongo_username()
app.config['MONGODB_PASSWORD'] = _config.get_mongo_password()
user_db = MongoEngine(app)


class Role(user_db.Document, RoleMixin):
    name = user_db.StringField(max_length=80, unique=True)
    description = user_db.StringField(max_length=255)


class User(user_db.Document, UserMixin):
    email = user_db.StringField(max_length=255)
    password = user_db.StringField(max_length=255)
    active = user_db.BooleanField(default=True)
    createAt = user_db.DateTimeField()
    roles = user_db.ListField(user_db.ReferenceField(Role), default=[])
    meta = {'strict': False}


# Setup Flask-Security
user_data_store = MongoEngineUserDatastore(user_db, User, Role)
security = Security(app, user_data_store)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return render_template('index.html')


from execution_engine.cron_job.cron_manager import CronManager

cron_manager = CronManager()
cron_manager.start()

from models import project, test_case, test_suite, test_suite_param, test_report, test_report_detail, test_env, \
    test_env_param, cron_job, data_source, leo_user, mail, mail_sender
from controllers import project, test_case, test_suite, test_suite_param, test_env, test_env_param, test_report, user, \
    cron_job, data_source, mail, mail_sender, init_admin_user

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=_config.get_port())
