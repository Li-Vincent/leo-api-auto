from utils.db.mongo_orm import *


class TempSuiteParams(Model):
    class Meta:
        database = db
        collection = 'tempSuiteParams'

    _id = ObjectIdField()
    testSuiteId = ObjectIdField(unique=True)
    params = DictField(field_name='params')
    updateTime = DateField()
    expiresTime = DateField()

    def __str__(self):
        return "_id:{} - testSuiteId: {} - params:{}".format(str(self._id), str(self.testSuiteId), str(self.params))


if __name__ == '__main__':
    pass
