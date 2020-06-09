from utils.db.mongo_orm import *


class Role(Model):
    class Meta:
        database = db
        collection = 'role'

    # Fields

    _id = ObjectIdField()
    name = StringField(unique=True)
    description = StringField()

    def __str__(self):
        return "name:{} - description:{}".format(self.name, self.description)


if __name__ == "__main__":
    pass
