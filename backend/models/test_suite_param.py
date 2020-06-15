from utils.db.mongo_orm import *

# Not yet used

class TestSuiteParam(Model):
    class Meta:
        database = db
        collection = 'testSuiteParam'

    # Fields
    _id = ObjectIdField()
    name = StringField(field_name='name', unique=True)
    paramValue = StringField()
    description = StringField()
    testSuiteId = ObjectIdField()
    status = BooleanField(field_name='status', default=False)
    projectId = ObjectIdField()
    isDeleted = BooleanField(field_name='isDeleted', default=False)
    createAt = DateField()
    lastUpdateTime = DateField()
    createUser = StringField()
    lastUpdateUser = StringField()

    def __str__(self):
        return "key:{} - value:{} - testSuiteId:{} - description:{} -  projectId:{}" \
            .format(self.name, self.paramValue, self.testSuiteId, self.description, self.projectId)


if __name__ == '__main__':
    pass
