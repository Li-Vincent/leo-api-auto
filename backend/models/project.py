from utils.db.mongo_orm import *


class Project(Model):
    class Meta:
        database = db
        collection = 'project'

    # Field
    _id = ObjectIdField()
    name = StringField()
    version = StringField()
    description = StringField()
    projectTestType = StringField()
    status = BooleanField(field_name='status', default=True)
    isDeleted = BooleanField(field_name='isDeleted', default=False)
    createAt = DateField()
    lastUpdateTime = DateField()
    createUser = StringField()
    lastUpdateUser = StringField()

    # 性能测试字段
    loopNum = IntField()
    mailList = ListField()
    domain = StringField()

    def __str__(self):
        return "name:{} - version:{} - description:{} - projectTestType:{} - status:{}".format(self.name, self.version,
                                                                                               self.description,
                                                                                               self.projectTestType,
                                                                                               self.status)


if __name__ == '__main__':
    pass
