import pytz
from bson import ObjectId
from flask import jsonify

from config import Config
from controllers.mail_sender import send_cron_email
from controllers.mail import get_mails_by_group
from controllers.env_config import get_env_name_and_domain
from controllers.test_env_param import get_global_env_vars
from controllers.test_report import save_report
from execution_engine.execution import execute_test_by_suite
from utils import common

config = Config()
host_ip = config.get_host()
host_port = config.get_port()


class Cron:

    def __init__(self, test_suite_id_list, project_id, test_env_id, trigger_type, include_forbidden=False,
                 always_send_mail=False, alarm_mail_group_list=None, is_web_hook=False, **trigger_args):

        if not isinstance(test_suite_id_list, list) or len(test_suite_id_list) < 1:
            raise TypeError('test_suite_id_list must be list and not empty！')

        if not test_env_id:
            raise ValueError('test_env_id should not be empty.')

        if not isinstance(trigger_type, str) or trigger_type not in ["interval", "date", "cron"]:
            raise TypeError('trigger_type is invalid!')

        # cronJob ID
        self._id = str(common.get_object_id())
        self.test_suite_id_list = test_suite_id_list
        self.project_id = project_id
        self.test_env_id = test_env_id
        self.trigger_type = trigger_type
        self.include_forbidden = include_forbidden
        self.trigger_args = trigger_args
        self.status_history = {}
        self.always_send_mail = always_send_mail
        self.alarm_mail_group_list = alarm_mail_group_list
        self.is_web_hook = is_web_hook
        self.execution_mode = 'cronJob'

    def cron_mission(self):
        (env_name, protocol, domain) = get_env_name_and_domain(self.test_env_id)
        if not protocol or not domain or not env_name:
            return jsonify({'status': 'failed', 'data': '测试环境配置存在问题，请前往环境设置检查'})

        global_env_vars = get_global_env_vars(self.test_env_id)
        alarm_mail_list = []
        if self.alarm_mail_group_list:
            if isinstance(self.alarm_mail_group_list, list) and len(self.alarm_mail_group_list) > 0:
                alarm_mail_list = get_mails_by_group(self.alarm_mail_group_list)
            else:
                raise TypeError('alarm_mail_group_list must be list')
        # 根据时间生成一个ObjectId作为reportId
        report_id = str(common.get_object_id())
        test_report = {'_id': ObjectId(report_id),
                       'testEnvId': ObjectId(self.test_env_id),
                       'testEnvName': env_name,
                       'executionMode': self.execution_mode}
        if self._id:
            test_report['cronJobId'] = ObjectId(self._id)
        if self.project_id:
            test_report['projectId'] = ObjectId(self.project_id)
        try:
            test_report_returned = execute_test_by_suite(report_id, test_report, self.test_env_id,
                                                         self.test_suite_id_list, protocol, domain,
                                                         global_env_vars)
            save_report(test_report_returned)
            if test_report_returned['totalCount'] > 0:
                is_send_mail = ((self.always_send_mail
                                 and isinstance(alarm_mail_list, list) and len(alarm_mail_list) > 0)
                                or (test_report_returned['totalCount'] > test_report_returned['passCount']
                                    and isinstance(alarm_mail_list, list) and len(alarm_mail_list) > 0))
                if is_send_mail:
                    subject = 'Leo API Auto Test Notify'
                    content_result = "<font color='green'>PASS</font>"
                    if test_report_returned['totalCount'] > test_report_returned['passCount']:
                        content_result = "<font color='red'>FAIL</font>"
                    notify_total_count = test_report_returned['totalCount']
                    notify_pass_count = test_report_returned['passCount']
                    notify_pass_rate = '{:.2%}'.format(notify_pass_count / notify_total_count)
                    content = "<h2>Dears:</h2>" \
                              "<div style='font-size:20px'>&nbsp;&nbsp;API Test CronJob executed successfully!<br/>" \
                              "&nbsp;&nbsp;Cron Job ID:&nbsp;&nbsp; <b>{}</b><br/>" \
                              "&nbsp;&nbsp;Environment:&nbsp;&nbsp; <b>{}</b><br/>" \
                              "&nbsp;&nbsp;Status:&nbsp;&nbsp; <b>{}</b><br/>" \
                              "&nbsp;&nbsp;TotalAPICount:&nbsp;&nbsp; <b>{}</b><br/>" \
                              "&nbsp;&nbsp;PassAPICount:&nbsp;&nbsp; <b>{}</b><br/>" \
                              "&nbsp;&nbsp;PassRate:&nbsp;&nbsp; <b>{}</b><br/>" \
                              "&nbsp;&nbsp;<a href=\"http://{}:{}/project/{}/testReport/{}\">Please login platform " \
                              "for details!</a><br/>" \
                              "&nbsp;&nbsp;Report ID: {}<br/>" \
                              "&nbsp;&nbsp;Generated At: {} CST</div>" \
                        .format(self._id, env_name, content_result, notify_total_count, notify_pass_count,
                                notify_pass_rate, host_ip, host_port, self.project_id, report_id, report_id,
                                test_report_returned['createAt'].replace(tzinfo=pytz.utc).astimezone(
                                    pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S'))
                    mail_result = send_cron_email(alarm_mail_list, subject, content)
                    if mail_result.get('status') == 'failed':
                        raise BaseException('邮件发送异常: {}'.format(mail_result.get('data')))
            else:
                raise TypeError('无任何测试结果！')
        except BaseException as e:
            return False, "出错了 - %s" % e

    def get_cron_job_id(self):
        return self._id
