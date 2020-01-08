from pymongo import MongoClient, errors, results
from bson import ObjectId
import datetime
from utils import common


def get_mongo_connection(host='127.0.0.1', port=27017, username=None, password=None):
    connection = MongoClient(host, port)
    if username and password:
        connection.admin.authenticate(username, password)
    return connection


def close_mongo_connection(connection):
    connection.close()


def get_database(connection, database):
    return connection.get_database(database)


def check_db_connect(database, host='127.0.0.1', port=27017, username=None, password=None):
    """Check Mongo DB Can be connected"""
    client = MongoClient(host, port)
    if username and password:
        client.admin.authenticate(username, password)
    if client:
        db_list = client.list_database_names()
        return True if database in db_list else False
    else:
        return False


def insert_one(database, collection, document):
    if not database:
        raise ValueError("db is empty")
    if not collection:
        raise ValueError("collection is None")
    if document and not isinstance(document, dict):
        raise TypeError("document should be a dict")
    try:
        inserted_result = database[collection].insert_one(document)
        if isinstance(inserted_result, results.InsertOneResult):
            return True, inserted_result.inserted_id
    except BaseException as e:
        return False, e


def insert_many(database, collection, documents):
    if not database:
        raise ValueError("db is empty")
    if not collection:
        raise ValueError("collection is None")
    if documents and not isinstance(documents, list):
        raise TypeError("documents should be a list")
    for document in documents:
        if not isinstance(document, dict):
            raise TypeError("document should be a dict")
    try:
        inserted_result = database[collection].insert_many(documents)
        if isinstance(inserted_result, results.InsertManyResult):
            return True, inserted_result.inserted_ids
        return True, _ids
    except BaseException as e:
        return False, e


def update_one(database, collection, query_dict, set_dict):
    if not database:
        raise ValueError("db is empty")
    if not collection:
        raise ValueError("collection is None")
    if query_dict and not isinstance(query_dict, dict):
        raise TypeError("query_dict should be a dict")
    if set_dict and not isinstance(set_dict, dict):
        raise TypeError("set_dict should be a dict")
    try:
        update_resulted = database[collection].update_one(query_dict, {'$set': set_dict})
        if isinstance(update_resulted, results.UpdateResult):
            return True, update_resulted.raw_result['n']
        else:
            return True, update_resulted
    except BaseException as e:
        return False, e


def update_many(database, collection, query_dict, set_dict):
    if not database:
        raise ValueError("db is empty")
    if not collection:
        raise ValueError("collection is None")
    if query_dict and not isinstance(query_dict, dict):
        raise TypeError("query_dict should be a dict")
    if set_dict and not isinstance(set_dict, dict):
        raise TypeError("set_dict should be a dict")
    try:
        update_resulted = database[collection].update_many(query_dict, {'$set': set_dict})
        if isinstance(update_resulted, results.UpdateResult):
            return True, update_resulted.raw_result['n']
        else:
            return True, update_resulted
    except BaseException as e:
        return False, e


if __name__ == '__main__':
    pass
    # print(check_db_connect('test'))
    # connection = get_mongo_connection()
    # db = get_database(connection, 'leo-api-auto-db')
    # col_name = 'host'
    # query = {'_id': ObjectId('5dd65212160e05d8aff7eead')}
    # update_dict = {'status': False}
    # result, count = update_many(db, col_name, query, update_dict)
    # print(result, count)
    # insert_dict = [{
    #     "isDeleted": True,
    #     "status": False,
    #     "name": "test  insert one",
    #     "host": "127.0.0.1:8888",
    #     "description": "test   add",
    #     "projectId": ObjectId("5dce1489a79ddf868dc4bcd8")
    # }, {"isDeleted": True,
    #     "status": False,
    #     "name": "test  insert many",
    #     "host": "127.0.0.1:8888",
    #     "description": "test   add",
    #     "projectId": ObjectId("5dce1489a79ddf868dc4bcd8")
    #     }]
    # result, insert_id = insert_many(db, col_name, insert_dict)
    # print(result, insert_id)
    # connection.close()
