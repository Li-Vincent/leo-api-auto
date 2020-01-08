from utils.db.mongo_orm import *


class Mail(Model):
    class Meta:
        database = db
        collection = 'mail'

    # Fields
    _id = ObjectIdField()
    name = StringField()
    projectId = ObjectIdField()
    email = StringField()
    description = StringField()
    status = BooleanField(field_name='status', default=False)
    createAt = DateField()
    createUser = StringField()
    lastUpdateTime = DateField()
    lastUpdateUser = StringField()

    def __str__(self):
        return "name:{} - email:{} - description:{} - status:{}".format(self.name, self.email, self.description,
                                                                        self.status)


if __name__ == '__main__':
    pass
