from datetime import datetime

from bson import ObjectId
from flask import jsonify, request, current_app
from flask_security import login_required, roles_accepted

from app import app
from controllers.env_config import get_env_name_and_domain
from models.plan import Plan
from models.test_suite import TestSuite
from utils import common
from execution_engine.execution import execute_plan_async, get_project_execution_range


@app.route('/api/plan/planList', methods=['GET'])
@login_required
def plan_list():
    total_num, plans = common.get_total_num_and_arranged_data(Plan, request.args, fuzzy_fields=['name'])
    return jsonify({'status': 'ok', 'data': {'totalNum': total_num, 'rows': plans}})


@app.route('/api/plan/<plan_id>', methods=['GET'])
@login_required
def get_plan(plan_id):
    res = Plan.find_one({'_id': ObjectId(plan_id)})
    return jsonify({'status': 'ok', 'data': common.format_response_in_dic(res)})


@app.route('/api/plan/addPlan', methods=['POST'])
@login_required
@roles_accepted('admin', 'project')
def add_plan():
    try:
        params = request.get_json()
        params['createAt'] = datetime.utcnow()
        params['status'] = False
        filtered_data = Plan.filter_field(params, use_set_default=True)
        Plan.insert(filtered_data)
        current_app.logger.info("add plan successfully. Plan: %s" % str(filtered_data['name']))
        return jsonify({'status': 'ok', 'data': '新建成功'})
    except BaseException as e:
        current_app.logger.error("add plan failed. - %s" % str(e))
        return jsonify({'status': 'failed', 'data': '新建失败 %s' % e})


@app.route('/api/plan/<plan_id>/updatePlan', methods=['POST'])
@login_required
@roles_accepted('admin', 'project')
def update_plan(plan_id):
    try:
        request_data = request.get_json()
        request_data['lastUpdateTime'] = datetime.utcnow()
        if 'enableWXWorkNotify' in request_data and request_data['enableWXWorkNotify']:
            if 'WXWorkAPIKey' not in request_data or not request_data['WXWorkAPIKey']:
                return jsonify({'status': 'failed', 'data': '请设置企业微信APIKey！'})
        if 'enableDingTalkNotify' in request_data and request_data['enableDingTalkNotify']:
            if 'DingTalkAccessToken' not in request_data or not request_data['DingTalkAccessToken']:
                return jsonify({'status': 'failed', 'data': '请设置钉钉AccessToken！'})
        filtered_data = Plan.filter_field(request_data)
        update_response = Plan.update({'_id': ObjectId(plan_id)}, {'$set': filtered_data})
        if update_response["n"] == 0:
            return jsonify({'status': 'failed', 'data': '未找到相应更新数据！'})
        current_app.logger.info("update plan successfully. Plan ID: %s" % str(plan_id))
        return jsonify({'status': 'ok', 'data': '更新成功'})
    except BaseException as e:
        current_app.logger.error("update plan failed. - %s" % str(e))
        return jsonify({'status': 'failed', 'data': '更新失败: %s' % e})


def get_plan_detail(plan_id):
    res = Plan.find_one({'_id': ObjectId(plan_id)})
    return common.format_response_in_dic(res)


def get_is_parallel_and_execution_range(plan_id):
    res = common.format_response_in_dic(Plan.find_one({'_id': ObjectId(plan_id)}))
    is_parallel = res.get("isParallel")
    execution_range = list(map(get_project_execution_range, res.get("executionRange")))
    return is_parallel, execution_range


def validate_plan_id(plan_id):
    try:
        res = common.format_response_in_dic(Plan.find_one({'_id': ObjectId(plan_id)}))
        execution_range = list(map(get_project_execution_range, res.get("executionRange")))
        if len(execution_range) < 1:
            return False
        else:
            return True
    except BaseException as e:
        with app.app_context():
            current_app.logger.error("validate plan_id error, plan_id: {}, error:{}".format(plan_id, str(e)))
        return False


@app.route('/api/plan/<plan_id>/executePlanByManual', methods=['POST'])
@login_required
@roles_accepted('admin', 'project')
def execute_plan_by_manual(plan_id):
    content_type = request.headers.get("Content-Type")
    if "form" in content_type:
        request_data = request.form.to_dict()
    elif "json" in content_type:
        request_data = request.json
    if 'testEnvId' not in request_data or not request_data['testEnvId']:
        return jsonify({'status': 'failed', 'data': '尚未选择环境！'}), 400
    else:
        test_env_id = request_data["testEnvId"]
    if 'planId' in request_data:
        plan_id = request_data["planId"]
    if not validate_plan_id(plan_id):
        return jsonify({'status': 'failed', 'data': 'plan_id is invalid！'}), 400

    (env_name, protocol, domain) = get_env_name_and_domain(test_env_id)
    if not protocol or not domain or not env_name:
        return jsonify({'status': 'failed', 'data': '测试环境配置存在问题，请前往环境设置检查'})

    execution_mode = "planManual"
    execution_user = request_data["executionUser"]

    # 根据时间生成一个ObjectId作为reportId
    plan_report_id = str(common.get_object_id())
    test_plan_report = {
        '_id': ObjectId(plan_report_id),
        'planId': ObjectId(plan_id),
        'testEnvId': ObjectId(test_env_id),
        'testEnvName': env_name,
        'executionMode': execution_mode,
        'executionUser': execution_user
    }
    try:
        execute_plan_async(plan_id, plan_report_id, test_plan_report, test_env_id, env_name, protocol, domain,
                           execution_mode=execution_mode)
        return jsonify({'status': 'ok', 'data': "测试已成功启动，请稍后前往「测试计划报告」查看报告"})
    except BaseException as e:
        current_app.logger.error("execute_plan_by_manual failed. - %s" % str(e))
        return jsonify({'status': 'failed', 'data': "出错了 - %s" % e})


def check_secret_for_plan(plan_id, secret_key):
    try:
        res = Plan.find_one({"_id": ObjectId(plan_id)})
        secret_token = common.format_response_in_dic(res).get("secretToken")
        return True if secret_key == secret_token else False
    except BaseException as e:
        with app.app_context():
            current_app.logger.error("check_secret_for_plan failed. - %s" % str(e))
        return False


@app.route('/api/plan/<plan_id>/executePlanByWebHook', methods=['POST'])
def execute_plan_by_web_hook(plan_id):
    content_type = request.headers.get("Content-Type")
    if "form" in content_type or "urlencoded" in content_type:
        request_data = request.form.to_dict()
    elif "json" in content_type:
        request_data = request.json
    if 'testEnvId' not in request_data or not request_data['testEnvId']:
        return jsonify({'status': 'failed', 'data': '尚未选择环境！'}), 400
    else:
        test_env_id = request_data["testEnvId"]
    if 'planId' in request_data:
        plan_id = request_data["planId"]
    if not validate_plan_id(plan_id):
        return jsonify({'status': 'failed', 'data': 'plan_id is invalid！'}), 400
    if "secretToken" not in request_data or not request_data['secretToken']:
        return jsonify({'status': 'failed', 'data': '请提供secretToken！'}), 400
    if not check_secret_for_plan(plan_id, request_data["secretToken"]):
        return jsonify({'status': 'failed', 'data': 'secretToken校验失败！'}), 400
    (env_name, protocol, domain) = get_env_name_and_domain(test_env_id)
    if not protocol or not domain or not env_name:
        return jsonify({'status': 'failed', 'data': '测试环境配置存在问题，请前往环境设置检查'}), 500

    execution_mode = "webHook"
    execution_remark = request_data["executionRemark"]

    # 根据时间生成一个ObjectId作为reportId
    plan_report_id = str(common.get_object_id())
    test_plan_report = {
        '_id': ObjectId(plan_report_id),
        'planId': ObjectId(plan_id),
        'testEnvId': ObjectId(test_env_id),
        'testEnvName': env_name,
        'executionMode': execution_mode,
        'executionRemark': execution_remark
    }
    try:
        execute_plan_async(plan_id, plan_report_id, test_plan_report, test_env_id, env_name, protocol, domain,
                           execution_mode=execution_mode)
        return jsonify({'status': 'ok', 'data': "测试已成功启动，请稍后前往「测试计划报告」查看报告"})
    except BaseException as e:
        current_app.logger.error("execute_plan_by_web_hook failed. - %s" % str(e))
        return jsonify({'status': 'failed', 'data': "出错了 - %s" % e})
