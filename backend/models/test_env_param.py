from utils.db.mongo_orm import *


class TestEnvParam(Model):
    class Meta:
        database = db
        collection = 'testEnvParam'

    # Fields
    _id = ObjectIdField()
    name = StringField(field_name='name')
    paramValue = StringField(field_name='paramValue')
    testEnvId = ObjectIdField()
    description = StringField()
    status = BooleanField(field_name='status', default=False)
    projectId = ObjectIdField()
    isDeleted = BooleanField(field_name='isDeleted', default=False)
    createAt = DateField()
    lastUpdateTime = DateField()
    createUser = StringField()
    lastUpdateUser = StringField()

    def __str__(self):
        return "key:{} - value:{} - testEnvId:{} - description:{} -  projectId:{}" \
            .format(self.key, self.value, self.testEnvId, self.description, self.projectId)


if __name__ == '__main__':
    pass
