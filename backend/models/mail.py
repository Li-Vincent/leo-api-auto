from utils.db.mongo_orm import *


class MailRecipient(Model):
    class Meta:
        database = db
        collection = 'mailRecipient'

    # Fields
    _id = ObjectIdField()
    name = StringField()
    email = StringField()
    mailGroupId = ObjectIdField()
    description = StringField()
    status = BooleanField(field_name='status', default=False)
    createAt = DateField()
    createUser = StringField()
    lastUpdateTime = DateField()
    lastUpdateUser = StringField()

    def __str__(self):
        return "name:{} - email:{} - description:{} - status:{}".format(self.name, self.email, self.description,
                                                                        self.status)


class MailGroup(Model):
    class Meta:
        database = db
        collection = 'mailGroup'

    # Fields
    _id = ObjectIdField()
    name = StringField()
    description = StringField()
    status = BooleanField(field_name='status', default=False)
    createAt = DateField()
    createUser = StringField()
    lastUpdateTime = DateField()
    lastUpdateUser = StringField()

    def __str__(self):
        return "name:{} - email:{} - description:{} - status:{}".format(self.name, self.email, self.description,
                                                                        self.status)


class MailSender(Model):
    class Meta:
        database = db
        collection = 'mailSender'

    # Fields
    _id = ObjectIdField()
    name = StringField()
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
    pass
