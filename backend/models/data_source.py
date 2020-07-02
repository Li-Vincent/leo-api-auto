from utils.db.mongo_orm import *


class DBConfig(Model):
    class Meta:
        database = db
        collection = 'DBConfig'

    # Fields
    _id = ObjectIdField()
    name = StringField()
    dbType = StringField()
    description = StringField()
    status = BooleanField(field_name='status', default=True)
    isDeleted = BooleanField(field_name='isDeleted', default=False)
    createAt = DateField()
    lastUpdateTime = DateField()
    createUser = StringField()
    lastUpdateUser = StringField()

    def __str__(self):
        return "name:{} - dbType:{} - description:{} - status:{}" \
            .format(self.name, self.dbType, self.description, self.status)


class DBEnvConnect(Model):
    class Meta:
        database = db
        collection = 'DBEnvConnect'

    # Fields
    _id = ObjectIdField()
    dbConfigId = ObjectIdField()
    testEnvId = ObjectIdField()
    dbType = StringField()
    dbHost = StringField()
    dbPort = IntField()
    dbUser = StringField()
    dbPassword = StringField()
    dbName = StringField()
    createAt = DateField()
    lastUpdateTime = DateField()
    createUser = StringField()
    lastUpdateUser = StringField()

    def __str__(self):
        return "dbConfigId:{} - testEnvId:{} - dbHost:{} - dbName:{}" \
            .format(self.dbConfigId, self.testEnvId, self.dbHost, self.dbName)


if __name__ == '__main__':
    pass
