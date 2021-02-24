from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from flask import current_app
from pytz import timezone

from app import db, app
from execution_engine.cron_job.cron import Cron
from utils import common


class CronManager:

    def __init__(self, use_mongo_db=True):
        self.scheduler = BackgroundScheduler(timezone=timezone('Asia/Shanghai'))
        self.scheduler.configure()

        if use_mongo_db:
            self.job_store = MongoDBJobStore(database='apscheduler', collection='cronJob', client=db)
            self.scheduler.add_jobstore(self.job_store)
            self.is_replace_existing = True
        else:
            self.is_replace_existing = False

    def add_cron(self, cron_instance):
        try:
            if not isinstance(cron_instance, Cron):
                raise TypeError('please add correct cron!')
            if cron_instance.trigger_type == 'interval':
                seconds = cron_instance.trigger_args.get('seconds')
                if not isinstance(seconds, int) and not common.can_convert_to_int(seconds):
                    raise TypeError('please set correct time interval')
                seconds = int(seconds)
                if seconds <= 0:
                    raise ValueError('please set interval > 0')
                job = self.scheduler.add_job(func=cron_instance.cron_mission,
                                             trigger=cron_instance.trigger_type,
                                             seconds=seconds,
                                             replace_existing=self.is_replace_existing,
                                             coalesce=True,
                                             id=cron_instance.get_cron_job_id(),
                                             max_instances=5,
                                             jitter=0)
            elif cron_instance.trigger_type == 'date':
                run_date = cron_instance.trigger_args.get('run_date')
                # TODO 判断run_date类型
                job = self.scheduler.add_job(func=cron_instance.cron_mission,
                                             trigger=cron_instance.trigger_type,
                                             run_date=run_date,
                                             replace_existing=self.is_replace_existing,
                                             coalesce=True,
                                             id=cron_instance.get_cron_job_id())
            elif cron_instance.trigger_type == 'cron':
                raise TypeError('暂时不支持 trigger_type 等于 \'cron\'')

            return cron_instance.get_cron_job_id()
        except BaseException as e:
            with app.app_context():
                current_app.logger.error("add_cron failed. - %s" % str(e))

    def start(self, paused=False):
        self.scheduler.start(paused=paused)

    def pause_cron(self, cron_id=None, pause_all=False):
        if pause_all:
            self.scheduler.pause()
        elif cron_id:
            self.scheduler.pause_job(job_id=cron_id)

    def resume_cron(self, cron_id=None, resume_all=False):
        if resume_all:
            self.scheduler.resume()
        elif cron_id:
            self.scheduler.resume_job(job_id=cron_id)

    def del_cron(self, cron_id=None, del_all=False):
        if del_all:
            self.scheduler.remove_all_jobs()
        elif cron_id:
            self.scheduler.remove_job(job_id=cron_id)

    def update_cron(self, cron_job_id, project_id, cron_info):
        try:
            if not isinstance(cron_job_id, str):
                raise TypeError('cron_id must be str')

            if not isinstance(project_id, str):
                raise TypeError('project_id must be str')

            if not isinstance(cron_info, dict):
                raise TypeError('cron_info must be dict')

            trigger_type = cron_info.get('triggerType')
            interval = cron_info.get('interval')
            run_date = cron_info.get('runDate')
            test_suite_id_list = cron_info.get('testSuiteIdList')
            include_forbidden = cron_info.get('includeForbidden')
            test_env_id = cron_info.get('testEnvId')
            always_send_mail = cron_info.get('alwaysSendMail')
            alarm_mail_group_list = cron_info.get('alarmMailGroupList')
            enable_wxwork_notify = cron_info.get('enableWXWorkNotify')
            wxwork_api_key = cron_info.get('WXWorkAPIKey')
            wxwork_mention_mobile_list = cron_info.get('WXWorkMentionMobileList')
            always_wxwork_notify = cron_info.get('alwaysWXWorkNotify')
            enable_ding_talk_notify = cron_info.get('enableDingTalkNotify')
            ding_talk_access_token = cron_info.get('DingTalkAccessToken')
            ding_talk_at_mobiles = cron_info.get('DingTalkAtMobiles')
            ding_talk_secret = cron_info.get('DingTalkSecret')
            always_ding_talk_notify = cron_info.get('alwaysDingTalkNotify')

            if trigger_type == 'interval' and int(interval) > 0:
                self.scheduler.modify_job(job_id=cron_job_id, trigger=IntervalTrigger(seconds=interval))
            elif trigger_type == 'date':
                self.scheduler.modify_job(job_id=cron_job_id, trigger=DateTrigger(run_date=run_date))
            else:
                raise TypeError('更新定时任务触发器失败！')
            if run_date:
                cron = Cron(cron_job_id=cron_job_id,
                            test_suite_id_list=test_suite_id_list,
                            project_id=project_id,
                            test_env_id=test_env_id,
                            include_forbidden=include_forbidden,
                            enable_wxwork_notify=enable_wxwork_notify,
                            wxwork_api_key=wxwork_api_key,
                            wxwork_mention_mobile_list=wxwork_mention_mobile_list,
                            always_wxwork_notify=always_wxwork_notify,
                            enable_ding_talk_notify=enable_ding_talk_notify,
                            ding_talk_access_token=ding_talk_access_token,
                            ding_talk_at_mobiles=ding_talk_at_mobiles,
                            ding_talk_secret=ding_talk_secret,
                            always_ding_talk_notify=always_ding_talk_notify,
                            always_send_mail=always_send_mail,
                            alarm_mail_group_list=alarm_mail_group_list,
                            trigger_type=trigger_type,  # 更新定时器时，此参数并没有真正起到作用, 仅修改展示字段
                            run_date=run_date)  # 更新定时器时，此参数并没有起到作用, 仅修改展示字段
            else:
                cron = Cron(cron_job_id=cron_job_id,
                            test_suite_id_list=test_suite_id_list,
                            project_id=project_id,
                            include_forbidden=include_forbidden,
                            enable_wxwork_notify=enable_wxwork_notify,
                            wxwork_api_key=wxwork_api_key,
                            wxwork_mention_mobile_list=wxwork_mention_mobile_list,
                            always_wxwork_notify=always_wxwork_notify,
                            enable_ding_talk_notify=enable_ding_talk_notify,
                            ding_talk_access_token=ding_talk_access_token,
                            ding_talk_at_mobiles=ding_talk_at_mobiles,
                            ding_talk_secret=ding_talk_secret,
                            always_ding_talk_notify=always_ding_talk_notify,
                            test_env_id=test_env_id,
                            always_send_mail=always_send_mail,
                            alarm_mail_group_list=alarm_mail_group_list,
                            trigger_type=trigger_type,  # 更新定时器时，此参数并没有起到作用, 仅修改展示字段
                            seconds=interval)  # 更新定时器时，此参数并没有起到作用, 仅修改展示字段
            # 玄学，更改job的时候必须改args，不能改func
            self.scheduler.modify_job(job_id=cron_job_id, coalesce=True, args=[cron])
        except BaseException as e:
            with app.app_context():
                current_app.logger.error("update_cron failed. - %s" % str(e))

    def shutdown(self, force_shutdown=False):
        if force_shutdown:
            self.scheduler.shutdown(wait=False)
        else:
            self.scheduler.shutdown(wait=True)

    def get_jobs(self):
        return self.scheduler.get_jobs()


if __name__ == '__main__':
    pass
