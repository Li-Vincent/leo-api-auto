from utils.db.mongo_orm import *


class TestSuite(Model):
    class Meta:
        database = db
        collection = 'testSuite'

    _id = ObjectIdField()
    name = StringField()
    description = StringField()
    service = StringField()
    priority = StringField()
    sprint = StringField()
    storyId = StringField()
    testCaseId = StringField()
    projectId = ObjectIdField()
    isDeleted = BooleanField(field_name='isDeleted', default=False)
    status = BooleanField(field_name='status', default=False)
    createAt = DateField()
    createUser = StringField()
    lastUpdateTime = DateField()
    lastUpdateUser = StringField()

    def __str__(self):
        return "name:{} - projectId: {} - description:{}".format(self.name, self.projectId, self.description)


if __name__ == '__main__':
    pass
