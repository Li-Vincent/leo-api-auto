from datetime import datetime, timedelta

from bson import ObjectId
from flask import jsonify, request, current_app
from flask_security import login_required, roles_required

from app import app
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
        current_app.logger.error("save_report_detail failed. - %s" % str(e))
        return False


def save_report(test_report):
    filtered_data = TestReport.filter_field(test_report)
    try:
        TestReport.insert(filtered_data)
        return True
    except BaseException as e:
        current_app.logger.error("save_report failed. - %s" % str(e))
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


@app.route('/api/project/<project_id>/testReport/cleanReports', methods=['POST'])
@login_required
@roles_required('admin')
def clean_project_reports(project_id):
    try:
        request_data = request.get_json()
        operator = request_data.pop('operator')
        project_id = request_data.get('projectId')
        clean_date = request_data.get('cleanDate')
        execution_mode = request_data.get('executionMode')
        clean_dict = dict()
        clean_dict["projectId"] = project_id
        clean_dict["executionMode"] = execution_mode
        clean_dict["createAt"] = {"$lt": datetime.utcnow() - timedelta(days=clean_date)}
        total_num, reports = common.get_total_num_and_arranged_data(TestReport, clean_dict)
        clean_report_ids = list(map(lambda x: x.get("_id"), reports))
        if len(clean_report_ids):
            for clean_report_id in clean_report_ids:
                TestReport.delete_one({'_id': ObjectId(clean_report_id)})
                TestReportDetail.delete_many({'reportId': ObjectId(clean_report_id)})
            current_app.logger.info(
                "delete report successfully. Project ID:{},cleanDate:{},operator:{},deletedReportIds:{}".format(
                    project_id, clean_date, operator, str(clean_report_ids)))
            return jsonify({'status': 'ok', 'data': '删除报告成功'})
        else:
            current_app.logger.info(
                "no report need to be deleted. Project ID:{},cleanDate:{},operator:{}".format(project_id, clean_date,
                                                                                              operator))
            return jsonify({'status': 'ok', 'data': '未找到要删除的报告'})
    except BaseException as e:
        current_app.logger.error("delete report failed. - %s" % str(e))
        return jsonify({'status': 'failed', 'data': '删除报告失败: %s' % e})
