from utils.db.mongo_orm import *


# 类名定义 collection
class TestReportDetail(Model):
    class Meta:
        database = db
        collection = 'testReportDetail'

    # 字段
    _id = ObjectIdField()  # reportDetailId
    reportId = ObjectIdField()
    projectId = ObjectIdField()
    testSuiteId = ObjectIdField()
    testCaseId = ObjectIdField()
    resultDetail = DictField()
    createAt = DateField()

    def __str__(self):
        return "reportId:{} - testSuiteId:{} - testCaseId:{}".format(self.reportId, self.testSuiteId, self.testCaseId)


if __name__ == '__main__':
    pass
