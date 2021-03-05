from utils.db.mongo_orm import *


class LeoUser(Model):
    class Meta:
        database = db
        collection = 'user'

    # Fields

    _id = ObjectIdField()
    email = StringField(unique=True)
    password = StringField()
    active = BooleanField(field_name='active')
    roles = ListField()
    createAt = DateField()
    userProjects = ListField()

    def __str__(self):
        return "email:{} - password:{} -  roleIds:{}".format(self.email, self.password, self.roleIds)


if __name__ == "__main__":
    pass
