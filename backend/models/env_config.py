from utils.db.mongo_orm import *


class EnvConfig(Model):
    class Meta:
        database = db
        collection = 'EnvConfig'

    # Fields
    _id = ObjectIdField()
    name = StringField(field_name='name')
    protocol = StringField(field_name='protocol')
    domain = StringField(field_name='domain')
    description = StringField()
    status = BooleanField(field_name='status', default=False)
    isDeleted = BooleanField(field_name='isDeleted', default=False)
    createAt = DateField()
    lastUpdateTime = DateField()
    createUser = StringField()
    lastUpdateUser = StringField()

    def __str__(self):
        return "name:{} - protocol:{} - domain:{} - description:{} " \
            .format(self.name, self.protocol, self.domain, self.description)


if __name__ == '__main__':
    pass
