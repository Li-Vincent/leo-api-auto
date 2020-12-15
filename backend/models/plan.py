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
