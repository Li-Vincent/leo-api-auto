from datetime import datetime, timedelta

from bson import ObjectId
from flask import jsonify, request, current_app
from flask_security import login_required, roles_required

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
        with app.app_context():
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


@app.route('/api/plan/<plan_id>/cleanPlanReports', methods=['POST'])
@login_required
@roles_required('admin')
def clean_plan_reports(plan_id):
    try:
        request_data = request.get_json()
        operator = request_data.pop('operator')
        plan_id = request_data.get('planId')
        clean_date = request_data.get('cleanDate')
        clean_plan_report_dict = dict()
        clean_plan_report_dict["planId"] = plan_id
        clean_plan_report_dict["createAt"] = {"$lt": datetime.utcnow() - timedelta(days=clean_date)}
        total_num, plan_reports = common.get_total_num_and_arranged_data(TestPlanReport, clean_plan_report_dict)
        clean_plan_report_ids = list(map(lambda x: x.get("_id"), plan_reports))
        if len(clean_plan_report_ids):
            for clean_plan_report_id in clean_plan_report_ids:
                clean_report_dict = dict()
                clean_report_dict["planReportId"] = clean_plan_report_id
                total_num, reports = common.get_total_num_and_arranged_data(TestReport, clean_report_dict)
                clean_report_ids = list(map(lambda x: x.get("_id"), reports))
                for clean_report_id in clean_report_ids:
                    TestReportDetail.delete_many({'reportId': ObjectId(clean_report_id)})
                TestReport.delete_many({'planReportId': ObjectId(clean_plan_report_id)})
                TestPlanReport.delete_one({'_id': ObjectId(clean_plan_report_id)})
            current_app.logger.info(
                "delete report successfully. Plan ID:{},cleanDate:{},operator:{},deletedPlanReportIds:{}".format(
                    plan_id, clean_date, operator, str(clean_plan_report_ids)))
            return jsonify({'status': 'ok', 'data': '删除计划报告成功'})
        else:
            current_app.logger.info(
                "no report need to be deleted. Plan ID:{},cleanDate:{},operator:{}".format(plan_id, clean_date,
                                                                                           operator))
            return jsonify({'status': 'ok', 'data': '未找到要删除的计划报告'})
    except BaseException as e:
        current_app.logger.error("delete report failed. - %s" % str(e))
        return jsonify({'status': 'failed', 'data': '删除计划报告失败: %s' % e})
