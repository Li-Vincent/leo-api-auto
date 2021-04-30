#!/usr/bin/python
# -*- coding: utf-8 -*-
from datetime import datetime

from bson import ObjectId
from flask import jsonify, request, current_app
from flask_security import login_required, roles_accepted

from app import app, cron_manager
from models.cron_job import CronJob
from utils import common
from execution_engine.cron_job.cron import Cron


@app.route('/api/project/<project_id>/cronJobList', methods=['GET'])
@login_required
def cron_job_list(project_id):
    def time_stamp2str(cron):
        if cron.get('next_run_time'):
            cron['next_run_time'] = common.time_stamp2str(cron['next_run_time'])
        return cron

    total_num, cron_jobs = common.get_total_num_and_arranged_data(CronJob, request.args, fuzzy_fields=['name'])
    cron_jobs = list(map(time_stamp2str, cron_jobs))
    return jsonify({'status': 'ok', 'data': {'totalNum': total_num, 'rows': cron_jobs}})


@app.route('/api/project/<project_id>/addCronJob', methods=['POST'])
@login_required
@roles_accepted('admin', 'project')
def add_cron_job(project_id):
    try:
        request_data = request.get_json()
        request_data["projectId"] = ObjectId(project_id)
        request_data["testEnvId"] = ObjectId(request_data["testEnvId"])
        if "alarmMailGroupList" in request_data and len(request_data["alarmMailGroupList"]) > 0:
            for index, value in enumerate(request_data["alarmMailGroupList"]):
                request_data["alarmMailGroupList"][index] = ObjectId(value)
        request_data["createAt"] = datetime.utcnow()
        if 'interval' in request_data and request_data['interval'] < 60:
            return jsonify({'status': 'failed', 'data': '定时任务间隔不可小于60秒！'})

        if 'interval' in request_data:
            request_data['interval'] = float(request_data['interval'])

        if 'runDate' in request_data:
            request_data['runDate'] = common.frontend_date_str2datetime(request_data['runDate'])
        filtered_data = CronJob.filter_field(request_data, use_set_default=True)
        new_cron_job_id = str(common.get_object_id())
        if filtered_data.get('runDate'):
            cron = Cron(cron_job_id=new_cron_job_id,
                        test_suite_id_list=filtered_data.get('testSuiteIdList'),
                        project_id=project_id,
                        test_env_id=filtered_data.get('testEnvId'),
                        trigger_type=filtered_data.get('triggerType'),
                        include_forbidden=filtered_data.get('includeForbidden'),
                        enable_wxwork_notify=filtered_data.get('enableWXWorkNotify'),
                        wxwork_api_key=filtered_data.get('WXWorkAPIKey'),
                        wxwork_mention_mobile_list=filtered_data.get('WXWorkMentionMobileList'),
                        always_wxwork_notify=filtered_data.get('alwaysWXWorkNotify'),
                        enable_ding_talk_notify=filtered_data.get('enableDingTalkNotify'),
                        ding_talk_access_token=filtered_data.get('DingTalkAccessToken'),
                        ding_talk_at_mobiles=filtered_data.get('DingTalkAtMobiles'),
                        ding_talk_secret=filtered_data.get('DingTalkSecret'),
                        always_ding_talk_notify=filtered_data.get('alwaysDingTalkNotify'),
                        alarm_mail_group_list=filtered_data.get('alarmMailGroupList'),
                        always_send_mail=filtered_data.get('alwaysSendMail'),
                        run_date=filtered_data.get('runDate'))
        else:
            cron = Cron(cron_job_id=new_cron_job_id,
                        test_suite_id_list=filtered_data.get('testSuiteIdList'),
                        project_id=project_id,
                        test_env_id=filtered_data.get('testEnvId'),
                        trigger_type=filtered_data.get('triggerType'),
                        include_forbidden=filtered_data.get('includeForbidden'),
                        enable_wxwork_notify=filtered_data.get('enableWXWorkNotify'),
                        wxwork_api_key=filtered_data.get('WXWorkAPIKey'),
                        wxwork_mention_mobile_list=filtered_data.get('WXWorkMentionMobileList'),
                        always_wxwork_notify=filtered_data.get('alwaysWXWorkNotify'),
                        enable_ding_talk_notify=filtered_data.get('enableDingTalkNotify'),
                        ding_talk_access_token=filtered_data.get('DingTalkAccessToken'),
                        ding_talk_at_mobiles=filtered_data.get('DingTalkAtMobiles'),
                        ding_talk_secret=filtered_data.get('DingTalkSecret'),
                        always_ding_talk_notify=filtered_data.get('alwaysDingTalkNotify'),
                        alarm_mail_group_list=filtered_data.get('alarmMailGroupList'),
                        always_send_mail=filtered_data.get('alwaysSendMail'),
                        seconds=filtered_data.get('interval'))
        cron_id = cron_manager.add_cron(cron)
        filtered_data['lastUpdateTime'] = datetime.utcnow()
        update_response = CronJob.update({"_id": cron_id}, {'$set': filtered_data})
        if update_response["n"] == 0:
            return jsonify({'status': 'failed', 'data': '新建成功但未找到相应更新数据！'})
        current_app.logger.info("add cron job successfully. New Cron Id: %s" % str(cron_id))
        return jsonify({'status': 'ok', 'data': '新建成功'})
    except BaseException as e:
        current_app.logger.error("add cron job failed. - %s" % str(e))
        return jsonify({'status': 'failed', 'data': '新建失败: %s' % e})


@app.route('/api/project/<project_id>/updateCronJob/<cron_job_id>', methods=['POST'])
@login_required
@roles_accepted('admin', 'project')
def update_cron_job(project_id, cron_job_id):
    data = request.get_json()
    if data and data.get('triggerType') == 'interval' and 'runDate' in data:
        data.pop('runDate')
    elif data and data.get('triggerType') == 'date' and 'interval' in data:
        data.pop('interval')

    if 'interval' in data:
        data['interval'] = float(data['interval'])

    if 'interval' in data and data['interval'] < 60:
        return jsonify({'status': 'failed', 'data': '定时任务间隔不可小于60秒！'})

    if 'runDate' in data:
        data['runDate'] = common.frontend_date_str2datetime(data['runDate'])

    has_next_run_time = True if 'next_run_time' in data and data.pop('next_run_time') else False  # 判断是否需要重启cron
    data["testEnvId"] = ObjectId(data["testEnvId"])
    if data["alarmMailGroupList"] and len(data["alarmMailGroupList"]) > 0:
        for index, value in enumerate(data["alarmMailGroupList"]):
            data["alarmMailGroupList"][index] = ObjectId(value)
    filtered_data = CronJob.filter_field(data)
    try:
        cron_manager.update_cron(cron_job_id=cron_job_id, project_id=project_id, cron_info=filtered_data)
        # update cronJob 自动停用，需点击启动后使用
        cron_manager.pause_cron(cron_id=cron_job_id)
        filtered_data['status'] = 'PAUSED'
        filtered_data['lastUpdateTime'] = datetime.utcnow()
        update_response = CronJob.update({"_id": cron_job_id},
                                         {'$set': filtered_data})
        if update_response["n"] == 0:
            return jsonify({'status': 'failed', 'data': '未找到相应更新数据！'})
        current_app.logger.info("update cron job successfully. Cron Job Id: %s" % str(cron_job_id))
        return jsonify({'status': 'ok', 'data': '更新成功'})
    except BaseException as e:
        current_app.logger.error("update cron job failed. - %s" % str(e))
        return jsonify({'status': 'failed', 'data': '更新失败: %s' % e})


@app.route('/api/project/<project_id>/pauseCronJob/<cron_job_id>', methods=['POST'])
@login_required
@roles_accepted('admin', 'project')
def pause_cron_job(project_id, cron_job_id):
    try:
        cron_manager.pause_cron(cron_id=cron_job_id)
        CronJob.update({"_id": cron_job_id},
                       {'$set': {'status': 'PAUSED'}})
        current_app.logger.info("pause cron job successfully. Cron Job Id: %s" % str(cron_job_id))
        return jsonify({'status': 'ok', 'data': '停用成功'})
    except BaseException as e:
        current_app.logger.error("pause cron job failed. - %s" % str(e))
        return jsonify({'status': 'ok', 'data': '停用失败: %s' % e})


@app.route('/api/project/<project_id>/deleteCronJob/<cron_job_id>', methods=['POST'])
@login_required
@roles_accepted('admin', 'project')
def del_cron_job(project_id, cron_job_id):
    try:
        cron_manager.del_cron(cron_id=cron_job_id)
        current_app.logger.info("del cron job successfully. Cron Job Id: %s" % str(cron_job_id))
        return jsonify({'status': 'ok', 'data': '删除成功'})
    except BaseException as e:
        current_app.logger.error("del cron job failed. - %s" % str(e))
        return jsonify({'status': 'ok', 'data': '删除失败: %s' % e})


@app.route('/api/project/<project_id>/resumeCronJob/<cron_job_id>', methods=['POST'])
@login_required
@roles_accepted('admin', 'project')
def resume_cron_job(project_id, cron_job_id):
    try:
        cron_manager.resume_cron(cron_id=cron_job_id)
        CronJob.update({"_id": cron_job_id},
                       {'$set': {'status': 'RESUMED'}})
        current_app.logger.info("resume cron job successfully. Cron Job Id: %s" % str(cron_job_id))
        return jsonify({'status': 'ok', 'data': '启动成功'})
    except BaseException as e:
        current_app.logger.error("resume cron job failed. - %s" % str(e))
        return jsonify({'status': 'ok', 'data': '启动失败: %s' % e})


@app.route('/api/project/<project_id>/cronJob/start', methods=['POST'])
@login_required
@roles_accepted('admin')
def start(project_id):
    try:
        data = request.get_json()
        if data:
            paused = data.get('paused')
        else:
            paused = None
        cron_manager.start(paused=paused)
        return jsonify({'status': 'ok', 'data': '调度器启动成功'})
    except BaseException as e:
        current_app.logger.error("start cron job failed. - %s" % str(e))
        return jsonify({'status': 'ok', 'data': '调度器启动失败: %s' % e})


@app.route('/api/project/<project_id>/cronJob/shutdown', methods=['POST'])
@login_required
@roles_accepted('admin')
def shutdown(project_id):
    try:
        data = request.get_json()
        force_shutdown = data.get('forceShutdown')
        cron_manager.shutdown(force_shutdown=force_shutdown)
        return jsonify({'status': 'ok', 'data': '调度器关闭成功'})
    except BaseException as e:
        current_app.logger.error("shutdown cron job failed. - %s" % str(e))
        return jsonify({'status': 'ok', 'data': '调度器关闭失败: %s' % e})
