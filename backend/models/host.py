from utils.db.mongo_orm import *


# 已弃用
class Host(Model):
    class Meta:
        database = db
        collection = 'host'

    # Fields
    _id = ObjectIdField()
    name = StringField()
    host = StringField()
    description = StringField()
    status = BooleanField(field_name='status', default=False)
    projectId = ObjectIdField()
    isDeleted = BooleanField(field_name='isDeleted', default=False)
    createAt = DateField()
    lastUpdateTime = DateField()
    createUser = StringField()
    lastUpdateUser = StringField()

    def __str__(self):
        return "name:{} - host:{} - description:{} - status:{} - projectId:{}" \
            .format(self.name, self.description, self.description, self.status, self.projectId)


if __name__ == '__main__':
    pass
