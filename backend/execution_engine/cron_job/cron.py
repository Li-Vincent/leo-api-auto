from bson import ObjectId
from flask import jsonify

from config import Config
from controllers.mail_sender import send_cron_email
from controllers.test_env import get_env_name_and_domain
from controllers.test_env_param import get_global_env_vars
from controllers.test_report import save_report
from execution_engine.execution import execute_test_by_suite
from utils import common

host_ip = common.get_host_ip()
host_port = Config().get_port()


class Cron:

    def __init__(self, test_suite_id_list, project_id, test_env_id, trigger_type, include_forbidden=False,
                 alarm_mail_list=None, is_web_hook=False, **trigger_args):

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

        self.alarm_mail_list = []
        if alarm_mail_list:
            if isinstance(alarm_mail_list, list):
                for alarm_mail in alarm_mail_list:
                    if isinstance(alarm_mail, str) and common.is_valid_email(alarm_mail):
                        self.alarm_mail_list.append(alarm_mail)
                    else:
                        raise TypeError('<%s> is invalid mail!' % alarm_mail)
            else:
                raise TypeError('mail_list must be list')

        self.is_web_hook = is_web_hook
        self.execution_mode = 'cronJob'

    def cron_mission(self):
        (env_name, domain) = get_env_name_and_domain(self.test_env_id)
        if not domain:
            return jsonify({'status': 'failed', 'data': '未找到任何「启用的」环境信息'})
        if not env_name:
            return jsonify({'status': 'failed', 'data': '测试环境名称为空，请设置环境名称'})

        global_env_vars = get_global_env_vars(self.test_env_id)

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
                                                         self.test_suite_id_list, domain,
                                                         global_env_vars)
            save_report(test_report_returned)
            if test_report_returned['totalCount'] > 0:
                is_send_mail = test_report_returned['totalCount'] > test_report_returned['passCount'] and isinstance(
                    self.alarm_mail_list, list) and len(self.alarm_mail_list) > 0
                print('========mail==========', is_send_mail)
                if is_send_mail:
                    subject = 'Leo API Auto Test'
                    content = "Dears:<br/>" \
                              "&nbsp;&nbsp;&nbsp;API test case failed!<br/>" \
                              "&nbsp;&nbsp;&nbsp;Please login platform for details!<br/>" \
                              "&nbsp;&nbsp;&nbsp;<a href=\"http://{}:{}/project/{}/testReport/{}\">Click here to see " \
                              "report detail!</a><br/>" \
                              "&nbsp;&nbsp;&nbsp;Report ID: {}<br/>" \
                              "&nbsp;&nbsp;&nbsp;Generated At: {}" \
                        .format(host_ip, host_port, self.project_id, report_id, report_id,
                                test_report_returned['createAt'].strftime('%Y-%m-%d %H:%M:%S'))
                    mail_result = send_cron_email(self.project_id, self.alarm_mail_list, subject, content)
                    if mail_result.get('status') == 'failed':
                        raise BaseException('邮件发送异常: {}'.format(mail_result.get('data')))
            else:
                raise TypeError('无任何测试结果！')
        except BaseException as e:
            return False, "出错了 - %s" % e

    def get_cron_job_id(self):
        return self._id


if __name__ == '__main__':
    pass
