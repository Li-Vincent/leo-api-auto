import json

from controllers.data_source import get_db_connect
from utils.common import replace_global_var_for_str
from utils.db.mongo_utils import *


def execute_data_init(test_env_id, data, global_vars):
    if data['dbConfigId'] and test_env_id:
        db_connect_config = get_db_connect(data['dbConfigId'], test_env_id)
        if db_connect_config['dbType'] == 'MongoDB':
            if 'dbUser' in db_connect_config and 'dbPassword' in db_connect_config:
                connection = get_mongo_connection(host=db_connect_config['dbHost'],
                                                  port=db_connect_config['dbPort'],
                                                  username=db_connect_config['dbUser'],
                                                  password=db_connect_config['dbPassword'])
            else:
                connection = get_mongo_connection(host=db_connect_config['dbHost'], port=db_connect_config['dbPort'])
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
            document_str = replace_global_var_for_str(init_var_str=json.dumps(data['set']), global_var_dic=global_vars) \
                if common.can_convert_to_str(data['set']) and isinstance(data['set'], dict) else None
            document_str = replace_global_var_for_str(init_var_str=document_str,
                                                      global_var_dic=global_vars,
                                                      global_var_regex=r'"\$num{.*?}"',
                                                      match2key_sub_string_start_index=6,
                                                      match2key_sub_string_end_index=-2
                                                      ) if document_str else None
            document = json.loads(document_str) if isinstance(document_str, str) and document_str.strip() else {}
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
                if status:
                    return {'status': 'ok', 'update_count': result, 'collection': data['collection'],
                            'query': query_str, 'set': document_str}
                else:
                    return {'status': 'failed', 'reason': result, 'collection': data['collection'],
                            'query': query_str, 'set': document_str}
            if data['mongoCrud'] and data['mongoCrud'] == 'insert_one':
                status, result = insert_one(database, data['collection'], document=document)
                if status:
                    return {'status': 'ok', 'insert_id': result, 'collection': data['collection'],
                            'document': document_str}
                else:
                    return {'status': 'failed', 'reason': result, 'collection': data['collection'],
                            'document': document_str}
            close_mongo_connection(connection)
    else:
        return {'status': 'ok', result: 'not support other than mongoDB yet'}
