from utils.db.mongo_orm import *


class EnvConfig(Model):
    class Meta:
        database = db
        collection = 'EnvConfig'

    # Fields
    _id = ObjectIdField()
    name = StringField(field_name='name')
    domain = StringField(field_name='domain')
    description = StringField()
    status = BooleanField(field_name='status', default=False)
    isDeleted = BooleanField(field_name='isDeleted', default=False)
    createAt = DateField()
    lastUpdateTime = DateField()
    createUser = StringField()
    lastUpdateUser = StringField()

    def __str__(self):
        return "name:{} - envKeyword:{} - description:{} - status:{} " \
            .format(self.name, self.envKeyword, self.description, self.status)


if __name__ == '__main__':
    pass
