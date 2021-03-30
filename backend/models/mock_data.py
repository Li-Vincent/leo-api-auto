from utils.db.mongo_orm import *


class MockData(Model):
    class Meta:
        database = db
        collection = 'mockData'

    # Fields
    _id = ObjectIdField()
    name = StringField()
    category = StringField()
    requestMethod = StringField()
    path = StringField()
    responseCode = StringField()
    responseBody = DictField()
    delaySeconds = FloatField(field_name='delaySeconds', default=0.0)
    description = StringField()
    status = BooleanField(field_name='status', default=False)
    isDeleted = BooleanField(field_name='isDeleted', default=False)
    createAt = DateField()
    createUser = StringField()
    lastUpdateTime = DateField()
    lastUpdateUser = StringField()
