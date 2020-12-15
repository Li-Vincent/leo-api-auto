from datetime import datetime

from bson import ObjectId
from flask import jsonify, request, current_app
from flask_security import login_required

from app import app
from models.plan import Plan
from models.test_plan_report import TestPlanReport
from models.test_report import TestReport
from models.test_report_detail import TestReportDetail
from models.project import Project
from utils import common


def save_plan_report(test_plan_report):
    filtered_data = TestPlanReport.filter_field(test_plan_report)
    try:
        TestPlanReport.insert(filtered_data)
        return True
    except BaseException as e:
        current_app.logger.error("save_plan_report failed. - %s" % str(e))
        return False


@app.route('/api/plan/<plan_id>/planReportList', methods=['GET'])
@login_required
def get_plan_report_list(plan_id):
    total_num, reports = common.get_total_num_and_arranged_data(TestPlanReport, request.args)
    return jsonify({'status': 'ok', 'data': {'totalNum': total_num, 'rows': reports}})


@app.route('/api/plan/planReport/<plan_report_id>', methods=['GET'])
@login_required
def get_plan_report_info(plan_report_id):
    res = TestPlanReport.find_one({'_id': ObjectId(plan_report_id)})
    res = common.format_response_in_dic(res)
    if res.get("planId"):
        res['planName'] = Plan.find_one({'_id': ObjectId(res.get("planId"))}).get('name')
    return jsonify({'status': 'ok', 'data': common.format_response_in_dic(res)}) if res else \
        jsonify({'status': 'failed', 'data': '未找到该report信息'})


@app.route('/api/plan/planReport/<plan_report_id>/detail', methods=['GET'])
@login_required
def get_plan_report_detail(plan_report_id):
    request_data = request.args.to_dict()
    request_data.setdefault("planReportId", ObjectId(plan_report_id))
    total_num, reports = common.get_total_num_and_arranged_data(TestReport, request_data)
    new_reports = list(map(set_project_name, reports))  # set projectName
    return jsonify({'status': 'ok', 'data': {'totalNum': total_num, 'rows': new_reports}})


@app.route('/api/plan/planReport/<plan_report_id>/project/<project_id>', methods=['GET'])
@login_required
def get_plan_project_report(plan_report_id, project_id):
    res = TestReport.find_one({'planReportId': ObjectId(plan_report_id), 'projectId': ObjectId(project_id)})
    return jsonify({'status': 'ok', 'data': common.format_response_in_dic(res)}) if res else \
        jsonify({'status': 'failed', 'data': '未找到该report信息'})


def set_project_name(project_report):
    if isinstance(project_report, dict):
        project_id = project_report.get("projectId")
        project = common.format_response_in_dic(Project.find_one({"_id": ObjectId(project_id)}))
        project_name = project.get("name") if project else "Get project name failed"
        project_report["projectName"] = project_name
    return project_report
