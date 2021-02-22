from utils.db.mongo_orm import *


class CronJob(Model):
    class Meta:
        database = db
        collection = 'apscheduler.cronJob'

    # Fields
    _id = StringField()
    projectId = ObjectIdField()
    name = StringField()
    description = StringField()
    testSuiteIdList = ListField()
    includeForbidden = BooleanField(field_name='includeForbidden', default=False)
    testEnvId = ObjectIdField()
    next_run_time = FloatField()
    triggerType = StringField()
    interval = FloatField()
    runDate = DateField()
    # 企业微信通知
    enableWXWorkNotify = BooleanField(field_name='enableWXWorkNotify', default=False)
    WXWorkAPIKey = StringField()  # 企业微信的apiKey
    WXWorkMentionMobileList = ListField(default=[])  # 手机号列表，提醒手机号对应的群成员
    alwaysWXWorkNotify = BooleanField(field_name='alwaysWXWorkNotify', default=False)
    # 邮件通知
    alarmMailGroupList = ListField()
    alwaysSendMail = BooleanField(field_name='alwaysSendMail', default=False)

    status = StringField(field_name='status', default='CREATED')
    isDeleted = BooleanField(field_name='isDeleted', default=False)
    createAt = DateField()
    createUser = StringField()
    lastUpdateTime = DateField()
    lastUpdateUser = StringField()

    def __str__(self):
        return 'name : {}, testSuiteIdList:{}'.format(self.name, self.testSuiteIdList)


if __name__ == '__main__':
    pass
