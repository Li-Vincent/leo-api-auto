from utils.db.mongo_orm import *


class TestCase(Model):
    class Meta:
        database = db
        collection = 'testCase'

    # Common Fields
    _id = ObjectIdField()
    name = StringField()
    description = StringField()
    isDeleted = BooleanField(field_name='isDeleted', default=False)
    status = BooleanField(field_name='status', default=False)
    projectId = ObjectIdField()
    testSuiteId = ObjectIdField()
    createAt = DateField()
    createUser = StringField()
    lastUpdateTime = DateField()
    lastUpdateUser = StringField()

    # 执行顺序
    sequence = IntField(field_name='sequence', default=0)
    # api content
    testCaseType = StringField()
    service = StringField(field_name='service')
    requestProtocol = StringField()
    requestMethod = StringField()
    domain = StringField()
    route = StringField()
    delaySeconds = IntField(field_name='delaySeconds', default=0)
    # 数据初始化
    dataInitializes = ListField(field_name='dataInitializes',
                                default=[{'dbConfigId': '', 'dbType': '', 'mongoCrud': '', 'collection': '',
                                          'query': '', 'set': '', 'sql': ''}],
                                expected_structure={
                                    'expectedTypeRange': [list],
                                    'expectedValueRange': [
                                        {
                                            'expectedTypeRange': [dict],
                                            'expectedDict': {
                                                'dbConfigId': {'expectedTypeRange': []},
                                                'dbType': {'expectedTypeRange': []},
                                                'mongoCrud': {'expectedTypeRange': []},
                                                'collection': {'expectedTypeRange': []},
                                                'query': {'expectedTypeRange': []},
                                                'set': {'expectedTypeRange': []},
                                                'sql': {'expectedTypeRange': []},
                                            }
                                        }
                                    ]
                                })
    headers = ListField(field_name='headers',
                        default=[
                            {'name': 'Accept', 'value': 'application/json'},
                            {'name': 'Content-Type', 'value': 'application/json'}
                        ],
                        expected_structure={
                            'expectedTypeRange': [list],
                            'expectedValueRange': [
                                {
                                    'expectedTypeRange': [dict],
                                    'expectedDict': {
                                        'name': {'expectedTypeRange': [str]},
                                        'value': {'expectedTypeRange': [str]}
                                    }
                                },
                                {
                                    'expectedTypeRange': [dict],
                                    'expectedDict': {
                                        'interrelate': {'expectedTypeRange': []},
                                        'name': {'expectedTypeRange': [str]},
                                        'value': {'expectedTypeRange': []}
                                    }
                                }
                            ]
                        })
    parameterType = StringField(field_name='service', default='json')  # json or form or file
    filePath = StringField()  # if parameterType = file, enable filePath
    requestBody = ListField(field_name='requestBody', default=[{}],
                            expected_structure={
                                'expectedTypeRange': [list],
                                'expectedValueRange': [{
                                    'expectedTypeRange': [dict],
                                    'expectedDict': {
                                    }
                                }]
                            })
    isJsonArray = BooleanField(field_name='isJsonArray', default=False)
    isClearCookie = BooleanField(field_name='isClearCookie', default=False)
    setGlobalVars = ListField(field_name='setGlobalVars',
                              default=[{'name': '', 'query': []}],
                              expected_structure={
                                  'expectedTypeRange': [list],
                                  'expectedValueRange': [{
                                      'expectedTypeRange': [dict],
                                      'expectedDict': {
                                          'name': {'expectedTypeRange': [str]},
                                          'query': {
                                              'expectedTypeRange': [list],
                                              'expectedValueRange': [
                                                  {'expectedTypeRange': [str]}
                                              ]
                                          }
                                      }
                                  }]
                              })

    # validate
    checkResponseCode = StringField()
    checkResponseBody = ListField(field_name='checkResponseBody',
                                  default=[{'regex': '', 'query': []}],
                                  expected_structure={
                                      'expectedTypeRange': [list, type(None)],
                                      'expectedValueRange': [{
                                          'expectedTypeRange': [dict],
                                          'expectedDict': {
                                              'regex': {'expectedTypeRange': [str]},
                                              'query': {
                                                  'expectedTypeRange': [list],
                                                  'expectedValueRange': [
                                                      {'expectedTypeRange': [str]}
                                                  ]
                                              }
                                          }
                                      }]
                                  })
    checkResponseNumber = ListField(field_name='checkResponseNumber',
                                    default=[{
                                        "expressions": {
                                            'firstArg': '',
                                            'operator': '',
                                            'secondArg': '',
                                            'judgeCharacter': '',
                                            'expectResult': ''
                                        }
                                    }],
                                    expected_structure={
                                        'expectedTypeRange': [list, type(None)],
                                        'expectedValueRange': [{
                                            'expectedTypeRange': [dict],
                                            'expectedDict': {
                                                'expressions': {
                                                    'expectedTypeRange': [dict],
                                                    'expectedDict': {
                                                        'firstArg': {'expectedTypeRange': [str]},
                                                        'operator': {'expectedTypeRange': [str]},
                                                        'secondArg': {'expectedTypeRange': [str]},
                                                        'judgeCharacter': {'expectedTypeRange': [str]},
                                                        'expectResult': {'expectedTypeRange': [str]}
                                                    }
                                                }
                                            }
                                        }]
                                    })
    checkSpendSeconds = IntField(field_name='checkSpendSeconds', default=0)
    testStatus = BooleanField(field_name='testStatus', default=False)  # 测试状态， true代表测试进行中
    lastManualResult = DictField(field_name='lastManualResult', default={})


def __str__(self):
    return "name: {}".format(self.name)


if __name__ == "__main__":
    pass
