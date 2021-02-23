from utils.db.mongo_orm import *


class Plan(Model):
    class Meta:
        database = db
        collection = 'plan'

    # Field
    _id = ObjectIdField()
    name = StringField()
    description = StringField()
    isParallel = BooleanField(field_name='isParallel', default=False)  # 是否多项目并行执行
    executionRange = ListField(field_name='executionRange',
                               default=[
                                   {'projectId': '', 'priority': 'ALL'}
                               ],
                               expected_structure={
                                   'expectedTypeRange': [list],
                                   'expectedValueRange': [
                                       {
                                           'expectedTypeRange': [dict],
                                           'expectedDict': {
                                               'projectId': {'expectedTypeRange': [str]},
                                               'priority': {'expectedTypeRange': [str]}
                                           }
                                       }]
                               })
    secretToken = StringField()  # webHook调用执行的token验证
    status = BooleanField(field_name='status', default=True)
    # 企业微信群通知
    enableWXWorkNotify = BooleanField(field_name='enableWXWorkNotify', default=False)
    WXWorkAPIKey = StringField()  # 企业微信的apiKey
    WXWorkMentionMobileList = ListField(default=[])  # 手机号列表，提醒手机号对应的群成员
    alwaysWXWorkNotify = BooleanField(field_name='alwaysWXWorkNotify', default=False)
    # 钉钉群通知
    enableDingTalkNotify = BooleanField(field_name='enableDingTalkNotify', default=False)
    DingTalkAccessToken = StringField()  # 钉钉机器人AccessToken
    DingTalkAtMobiles = ListField(default=[])  # 手机号列表，提醒手机号对应的群成员
    DingTalkSecret = StringField() # 钉钉机器人 加签密钥
    alwaysDingTalkNotify = BooleanField(field_name='alwaysDingTalkNotify', default=False)
    # 邮件通知
    alarmMailGroupList = ListField()
    alwaysSendMail = BooleanField(field_name='alwaysSendMail', default=False)

    isDeleted = BooleanField(field_name='isDeleted', default=False)
    createAt = DateField()
    lastUpdateTime = DateField()
    createUser = StringField()
    lastUpdateUser = StringField()

    def __str__(self):
        return "name:{} - description:{} - isParallel:{} - secretToken:{} ".format(self.name,
                                                                                   self.description,
                                                                                   self.isParallel,
                                                                                   self.secretToken)


if __name__ == '__main__':
    pass
