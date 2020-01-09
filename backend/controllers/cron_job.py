from datetime import datetime

from bson import ObjectId
from flask import jsonify, request
from flask_security import login_required, roles_accepted

from app_init import app, cron_manager
from models.cron_job import CronJob
from utils import common
from execution_engine.cron_job.cron import Cron


@app.route('/api/project/<project_id>/cronJob', methods=['GET'])
def cron_job(project_id):
    try:
        cron_instance = Cron(test_suite_id_list=["5de0b7d99a60185278ebaa18", "5dee6bf95bd992898c0955e8"],
                             project_id="5dce1489a79ddf868dc4bcd8",
                             test_env_id="5ddb892fbf51c7edf8ec1f4e",
                             trigger_type="interval",
                             alarm_mail_list=["liwh9@lenovo.com"])
        cron_instance.cron_mission()
        return jsonify({'status': 'ok'})
    except BaseException:
        return jsonify({'status': 'failed'})


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
        request_data["createAt"] = datetime.utcnow()
        if 'interval' in request_data and request_data['interval'] < 60:
            return jsonify({'status': 'failed', 'data': '定时任务间隔不可小于60秒！'})

        if 'interval' in request_data:
            request_data['interval'] = float(request_data['interval'])

        if 'runDate' in request_data:
            request_data['runDate'] = common.frontend_date_str2datetime(request_data['runDate'])
        filtered_data = CronJob.filter_field(request_data, use_set_default=True)
        if filtered_data.get('runDate'):
            cron = Cron(test_suite_id_list=filtered_data.get('testSuiteIdList'),
                        project_id=project_id,
                        test_env_id=filtered_data.get('testEnvId'),
                        trigger_type=filtered_data.get('triggerType'),
                        include_forbidden=filtered_data.get('includeForbidden'),
                        alarm_mail_list=filtered_data.get('alarmMailList'),
                        run_date=filtered_data.get('runDate'))
        else:
            cron = Cron(test_suite_id_list=filtered_data.get('testSuiteIdList'),
                        project_id=project_id,
                        test_env_id=filtered_data.get('testEnvId'),
                        trigger_type=filtered_data.get('triggerType'),
                        include_forbidden=filtered_data.get('includeForbidden'),
                        alarm_mail_list=filtered_data.get('alarmMailList'),
                        seconds=filtered_data.get('interval'))
        cron_id = cron_manager.add_cron(cron)
        filtered_data['lastUpdateTime'] = datetime.utcnow()
        update_response = CronJob.update({"_id": cron_id}, {'$set': filtered_data})
        if update_response["n"] == 0:
            return jsonify({'status': 'failed', 'data': '新建成功但未找到相应更新数据！'})
        return jsonify({'status': 'ok', 'data': '新建成功'})
    except BaseException as e:
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
    filtered_data = CronJob.filter_field(data)
    try:
        cron_manager.update_cron(cron_job_id=cron_job_id, project_id=project_id, cron_info=filtered_data)
        # TODO 仅修改名字/描述时，也重启了定时器，导致下一次运行时间变更, 解决成本有点大，暂不解决:)
        cron_manager.pause_cron(cron_id=cron_job_id)
        cron_manager.resume_cron(cron_id=cron_job_id)

        filtered_data['lastUpdateTime'] = datetime.utcnow()
        update_response = CronJob.update({"_id": cron_job_id},
                                         {'$set': filtered_data})
        if update_response["n"] == 0:
            return jsonify({'status': 'failed', 'data': '未找到相应更新数据！'})
        return jsonify({'status': 'ok', 'data': '更新成功'})
    except BaseException as e:
        return jsonify({'status': 'failed', 'data': '更新失败: %s' % e})


@app.route('/api/project/<project_id>/pauseCronJob/<cron_job_id>', methods=['POST'])
@login_required
@roles_accepted('admin', 'project')
def pause_cron_job(project_id, cron_job_id):
    try:
        cron_manager.pause_cron(cron_id=cron_job_id)
        CronJob.update({"_id": cron_job_id},
                       {'$set': {'status': 'PAUSED'}})
        return jsonify({'status': 'ok', 'data': '停用成功'})
    except BaseException as e:
        return jsonify({'status': 'ok', 'data': '停用失败: %s' % e})


@app.route('/api/project/<project_id>/deleteCronJob/<cron_job_id>', methods=['POST'])
@login_required
@roles_accepted('admin', 'project')
def del_cron_job(project_id, cron_job_id):
    try:
        cron_manager.del_cron(cron_id=cron_job_id)
        return jsonify({'status': 'ok', 'data': '删除成功'})
    except BaseException as e:
        return jsonify({'status': 'ok', 'data': '删除失败: %s' % e})


@app.route('/api/project/<project_id>/resumeCronJob/<cron_job_id>', methods=['POST'])
@login_required
@roles_accepted('admin', 'project')
def resume_cron_job(project_id, cron_job_id):
    try:
        cron_manager.resume_cron(cron_id=cron_job_id)
        CronJob.update({"_id": cron_job_id},
                       {'$set': {'status': 'RESUMED'}})
        return jsonify({'status': 'ok', 'data': '启动成功'})
    except BaseException as e:
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
        return jsonify({'status': 'ok', 'data': '调度器关闭失败: %s' % e})
