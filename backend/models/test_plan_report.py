from utils.db.mongo_orm import *


# 类名定义 collection
class TestPlanReport(Model):
    class Meta:
        database = db
        collection = 'testPlanReport'

    # 字段
    _id = ObjectIdField()  # planReportId
    planId = ObjectIdField() # planId
    totalCount = IntField()
    passCount = IntField()
    failCount = IntField()
    errorCount = IntField()
    testStartTime = DateField()
    spendTimeInSec = FloatField()
    testEnvId = ObjectIdField()
    testEnvName = StringField()
    executionMode = StringField()  # planManual / webHook
    executionUser = StringField()
    executionRemark = StringField()
    createAt = DateField()

    def __str__(self):
        return "_id:{} - planId:{} - totalCount:{} - passCount:{}".format(self._id, self.planId, self.totalCount,
                                                                             self.passCount)


if __name__ == '__main__':
    pass
