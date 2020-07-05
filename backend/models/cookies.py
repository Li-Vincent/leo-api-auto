from utils.db.mongo_orm import *


class Cookies(Model):
    class Meta:
        database = db
        collection = 'tempCookies'

    _id = ObjectIdField()
    testSuiteId = ObjectIdField(unique=True)
    cookies = ListField(field_name='cookies',
                        default=[{'name': '', 'value': ''}],
                        expected_structure={
                            'expectedTypeRange': [list],
                            'expectedValueRange': [{
                                'expectedTypeRange': [dict],
                                'expectedDict': {
                                    'name': {'expectedTypeRange': [str]},
                                    'value': {'expectedTypeRange': [str]}
                                }
                            }]
                        })
    updateTime = DateField()
    expiresTime = DateField()

    def __str__(self):
        return "_id:{} - testSuiteId: {} - cookies:{}".format(str(self._id), str(self.testSuiteId), str(self.cookies))


if __name__ == '__main__':
    pass
