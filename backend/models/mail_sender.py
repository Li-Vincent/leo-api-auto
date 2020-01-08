from utils.db.mongo_orm import *


class MailSender(Model):
    class Meta:
        database = db
        collection = 'mailSender'

    # Fields
    _id = ObjectIdField()
    name = StringField()
    projectId = ObjectIdField()
    email = StringField()
    password = StringField()
    SMTPServer = StringField()
    SMTPPort = IntField()
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
    MailSender.find({'projectId': ObjectId(project_id)})
    pass
