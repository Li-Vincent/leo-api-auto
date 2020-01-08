from datetime import datetime

from bson import ObjectId
from flask import jsonify, request
from flask_security import login_required

from app_init import app
from models.test_report import TestReport
from models.test_report_detail import TestReportDetail
from utils import common


def save_report_detail(report_id, test_suite_id, test_case_id, test_result):
    save_data = {
        "reportId": ObjectId(report_id),
        "testSuiteId": ObjectId(test_suite_id),
        "testCaseId": ObjectId(test_case_id),
        "createAt": datetime.utcnow(),
        "resultDetail": test_result
    }
    filtered_data = TestReportDetail.filter_field(save_data)
    try:
        TestReportDetail.insert(filtered_data)
        return True
    except BaseException as e:
        return False


def save_report(test_report):
    filtered_data = TestReport.filter_field(test_report)
    try:
        TestReport.insert(filtered_data)
        return True
    except BaseException as e:
        return False


@app.route('/api/project/<project_id>/testReportList', methods=['GET'])
@login_required
def get_report_list(project_id):
    total_num, reports = common.get_total_num_and_arranged_data(TestReport, request.args)
    return jsonify({'status': 'ok', 'data': {'totalNum': total_num, 'rows': reports}})


@app.route('/api/project/<project_id>/testReport/<report_id>', methods=['GET'])
@login_required
def get_report_info(project_id, report_id):
    res = TestReport.find_one({'_id': ObjectId(report_id)})
    return jsonify({'status': 'ok', 'data': common.format_response_in_dic(res)}) if res else \
        jsonify({'status': 'failed', 'data': '未找到该report信息'})


@app.route('/api/testReport/<report_id>/testSuite/<suite_id>', methods=['GET'])
@login_required
def get_test_case_reports(report_id, suite_id):
    total_num, reports = common.get_total_num_and_arranged_data(TestReportDetail, request.args)
    return jsonify({'status': 'ok', 'data': {'totalNum': total_num, 'rows': reports}})
