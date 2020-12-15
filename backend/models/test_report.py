from utils.db.mongo_orm import *


# 类名定义 collection
class TestReport(Model):
    class Meta:
        database = db
        collection = 'testReport'

    # 字段
    _id = ObjectIdField()  # reportId
    totalCount = IntField()
    passCount = IntField()
    failCount = IntField()
    errorCount = IntField()
    testStartTime = DateField()
    spendTimeInSec = FloatField()
    testSuites = DictField()  # suiteId / totalCount / passCount / failCount / errorCount
    projectId = ObjectIdField()
    testEnvId = ObjectIdField()
    testEnvName = StringField()
    executionMode = StringField()  # manual/ cronJob / planManual / webHook
    executionUser = StringField()
    cronJobId = ObjectIdField()
    createAt = DateField()
    isDeleted = BooleanField(field_name='isDeleted', default=False)
    lastUpdateTime = DateField()

    # add for plan execution report
    planReportId = ObjectIdField()

    def __str__(self):
        return "_id:{} - projectId:{} - totalCount:{} - passCount:{}".format(self._id, self.projectId, self.totalCount,
                                                                             self.passCount)


if __name__ == '__main__':
    pass
