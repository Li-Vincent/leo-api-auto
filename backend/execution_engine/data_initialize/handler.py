import json

from controllers.data_source import get_db_connect
from utils.common import replace_global_var_for_str
from utils.db.mongo_utils import *
from utils.db.mysql_utils import *


def execute_data_init(test_env_id, data, global_vars):
    try:
        if data['dbConfigId'] and test_env_id:
            db_connect_config = get_db_connect(data['dbConfigId'], test_env_id)
            if db_connect_config:
                if not (db_connect_config['dbHost'] and db_connect_config['dbPort'] and db_connect_config['dbName']):
                    return {'status': 'failed', 'result': 'db config 不完整'}
                if db_connect_config['dbType'] == 'MongoDB':
                    if 'dbUser' in db_connect_config and 'dbPassword' in db_connect_config:
                        connection = get_mongo_connection(host=db_connect_config['dbHost'],
                                                          port=db_connect_config['dbPort'],
                                                          username=db_connect_config['dbUser'],
                                                          password=db_connect_config['dbPassword'])
                    else:
                        connection = get_mongo_connection(host=db_connect_config['dbHost'],
                                                          port=db_connect_config['dbPort'])
                    database = get_database(connection, db_connect_config['dbName'])
                    query_str = common.replace_global_var_for_str(init_var_str=json.dumps(data['query']),
                                                                  global_var_dic=global_vars) \
                        if common.can_convert_to_str(data['query']) and isinstance(data['query'], dict) else None
                    query_str = common.replace_global_var_for_str(init_var_str=query_str,
                                                                  global_var_dic=global_vars,
                                                                  global_var_regex=r'"\$num{.*?}"',
                                                                  match2key_sub_string_start_index=6,
                                                                  match2key_sub_string_end_index=-2
                                                                  ) if query_str else None
                    query = json.loads(query_str) if isinstance(query_str, str) and query_str.strip() else {}
                    document_str = replace_global_var_for_str(init_var_str=json.dumps(data['set']),
                                                              global_var_dic=global_vars) \
                        if common.can_convert_to_str(data['set']) and isinstance(data['set'], dict) else None
                    document_str = replace_global_var_for_str(init_var_str=document_str,
                                                              global_var_dic=global_vars,
                                                              global_var_regex=r'"\$num{.*?}"',
                                                              match2key_sub_string_start_index=6,
                                                              match2key_sub_string_end_index=-2
                                                              ) if document_str else None
                    document = json.loads(document_str) if isinstance(document_str,
                                                                      str) and document_str.strip() else {}
                    if not document:
                        return {'status': 'failed', 'reason': "document is empty",
                                'collection': data['collection'],
                                'query': query, 'set': document}
                    if data['mongoCrud'] and data['mongoCrud'] == 'update_one' and query:
                        if not query:
                            return {'status': 'failed', 'reason': "query is empty",
                                    'collection': data['collection'],
                                    'query': query, 'set': document}
                        status, result = update_one(database, data['collection'], query_dict=query, set_dict=document)
                        close_mongo_connection(connection)
                        if status:
                            return {'status': 'ok', 'update_count': result, 'collection': data['collection'],
                                    'query': query_str, 'set': document_str}
                        else:
                            return {'status': 'failed', 'reason': result, 'collection': data['collection'],
                                    'query': query_str, 'set': document_str}
                    if data['mongoCrud'] and data['mongoCrud'] == 'update_many' and query:
                        if not query:
                            return {'status': 'failed', 'reason': "query is empty",
                                    'collection': data['collection'],
                                    'query': query_str, 'set': document_str}
                        status, result = update_many(database, data['collection'], query_dict=query,
                                                     set_dict=document)
                        close_mongo_connection(connection)
                        if status:
                            return {'status': 'ok', 'update_count': result, 'collection': data['collection'],
                                    'query': query_str, 'set': document_str}
                        else:
                            return {'status': 'failed', 'reason': result, 'collection': data['collection'],
                                    'query': query_str, 'set': document_str}
                    if data['mongoCrud'] and data['mongoCrud'] == 'insert_one':
                        status, result = insert_one(database, data['collection'], document=document)
                        close_mongo_connection(connection)
                        if status:
                            return {'status': 'ok', 'insert_id': result, 'collection': data['collection'],
                                    'document': document_str}
                        else:
                            return {'status': 'failed', 'reason': result, 'collection': data['collection'],
                                    'document': document_str}
                elif db_connect_config['dbType'] == 'MySQL':
                    if not db_connect_config['dbUser']:
                        return {'status': 'failed', 'result': 'dbUser is empty'}
                    connection = get_mysql_connection(host=db_connect_config['dbHost'],
                                                      port=db_connect_config['dbPort'],
                                                      user=db_connect_config['dbUser'],
                                                      password=db_connect_config['dbPassword'],
                                                      database=db_connect_config['dbName'])
                    sql = common.replace_global_var_for_str(init_var_str=data['sql'], global_var_dic=global_vars) \
                        if common.can_convert_to_str(data['sql']) else None
                    if not sql:
                        return {'status': 'failed', 'reason': "sql is empty", 'sql': sql}
                    status, result = execute(connection=connection, sql=sql)
                    if status:
                        return {'status': 'ok', 'affect_rows': result, 'sql': sql}
                    else:
                        return {'status': 'failed', 'reason': result, 'sql': sql}
                else:
                    return {'status': 'failed', 'result': 'not support other than MongoDB/MySQL yet'}
            else:
                return {'status': 'failed', 'reason': 'db_connect_config is None'}
    except BaseException as e:
        return {'status': 'failed', 'reason': e}
