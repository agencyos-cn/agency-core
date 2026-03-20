"""
MySQL Connector wrapper to use PyMySQL instead of mysql-connector-python
"""
import pymysql
from pymysql import Error as MySQLError
from contextlib import contextmanager


# 将 mysql.connector.Error 映射到 PyMySQL 的错误
Error = MySQLError


def connect(**kwargs):
    """
    连接函数，适配 mysql-connector-python 的参数到 PyMySQL
    """
    # 转换参数名称以适配 PyMySQL
    pymysql_kwargs = {}
    
    # 映射参数名称
    param_mapping = {
        'host': 'host',
        'port': 'port',
        'user': 'user',
        'password': 'password',
        'database': 'database',
        'charset': 'charset',
        'connect_timeout': 'connect_timeout',
        'read_timeout': 'read_timeout',
        'write_timeout': 'write_timeout'  # PyMySQL doesn't have a direct equivalent for write_timeout, using connect_timeout
    }
    
    for connector_param, pymysql_param in param_mapping.items():
        if connector_param in kwargs:
            pymysql_kwargs[pymysql_param] = kwargs[connector_param]
    
    # PyMySQL 需要 autocommit=True 来模拟 mysql-connector-python 的行为
    pymysql_kwargs['autocommit'] = False
    
    # 创建连接
    connection = pymysql.connect(**pymysql_kwargs)
    
    # 我们需要添加一些 mysql-connector-python 特有的属性
    # 为连接对象添加 is_connected 方法
    if not hasattr(connection, 'is_connected'):
        connection.is_connected = lambda: not connection.open
    
    if not hasattr(connection, 'commit'):
        connection.commit = connection.commit
    
    if not hasattr(connection, 'rollback'):
        connection.rollback = connection.rollback
    
    return connection


class MySQLConnection:
    """
    A wrapper class to simulate mysql-connector-python's connection object
    """
    def __init__(self, connection):
        self._conn = connection
    
    def cursor(self, dictionary=True):
        cursor_class = pymysql.cursors.DictCursor if dictionary else pymysql.cursors.Cursor
        return self._conn.cursor(cursor_class)
    
    def commit(self):
        self._conn.commit()
    
    def rollback(self):
        self._conn.rollback()
    
    def close(self):
        self._conn.close()
    
    def is_connected(self):
        return self._conn.open
    
    @property
    def autocommit(self):
        return self._conn.autocommit
    
    @autocommit.setter
    def autocommit(self, value):
        self._conn.autocommit(value)


def Connect(**kwargs):
    """
    与 mysql.connector.connect 相同的接口
    """
    conn = connect(**kwargs)
    return MySQLConnection(conn)