from utils.db.mongo_orm import *


class TestEnv(Model):
    class Meta:
        database = db
        collection = 'testEnv'

    # Fields
    _id = ObjectIdField()
    name = StringField(field_name='name')
    domain = StringField(field_name='domain')
    description = StringField()
    status = BooleanField(field_name='status', default=False)
    projectId = ObjectIdField()
    isDeleted = BooleanField(field_name='isDeleted', default=False)
    createAt = DateField()
    lastUpdateTime = DateField()
    createUser = StringField()
    lastUpdateUser = StringField()

    def __str__(self):
        return "name:{} - envKeyword:{} - description:{} - status:{} - projectId:{}" \
            .format(self.name, self.envKeyword, self.description, self.status, self.projectId)


if __name__ == '__main__':
    pass
