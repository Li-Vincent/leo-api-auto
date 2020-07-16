import pymysql
from utils import common


# add by Li-Vincent 20200716 for 支持MySQL 数据初始化

def get_mysql_connection(host='127.0.0.1', port=3306, user=None, password=None, database=None, charset=None):
    connection = pymysql.connect(host=host, port=port, user=user, password=password, database=database, charset=charset)
    return connection


def execute(connection, sql, args=None):
    try:
        cursor = connection.cursor()
        rows = cursor.execute(sql, args)
        cursor.close()
        connection.commit()
        connection.close()
        return True, rows
    except BaseException as e:
        return False, e


def execute_many(connection, sql, args=None):
    try:
        cursor = connection.cursor()
        rows = cursor.executemany(sql, args)
        cursor.close()
        connection.commit()
        connection.close()
        return True, rows
    except BaseException as e:
        return False, e


if __name__ == '__main__':
    # print("获取数据库连接")
    # conn = get_mysql_connection(host="127.0.0.1", user="root", password="admin", database="leo-auto-report")
    # SQL1 = "INSERT INTO user VALUES (1,'Tom1','test1@leo.com','nothing'),(2,'Tom2','test2@leo.com','nothing')"
    # SQL = "UPDATE user SET description='6666' WHERE username like 'Tom%'"
    # print("执行SQL")
    # status, res = execute(connection=conn, sql=SQL)
    # if status:
    #     print("执行成功，影响条数为", res)
    # if not status:
    #     print("执行出错，原因：", res)
    pass
