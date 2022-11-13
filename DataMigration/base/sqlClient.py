# !/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:lupengliang
import pymysql

class MyClient:

    """
    database: 指单个数据库，并非列表
    """
    def __init__(self, username, password, database, host, port: int):
        self.username = username
        self.password = password
        self.database = database
        self.host = host
        self.port = port
        self.conn = pymysql.connect(user=self.username, password=self.password, database=self.database, host=self.host, port=self.port)
        self.cursor = self.conn.cursor()

    # 查一条
    def select_one(self, sql):
        """
        :param sql: select count(*) from table_name; 获取表中记录数
        :return:
        """
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchone()
            return result
        except:
            pass
        finally:
            pass

    # 查所有
    def select_all(self, sql):
        """
        :param sql: select count(*) from table_name; 获取表中记录数
        :return:
        """
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            return result
        except:
            pass
        finally:
            pass

    # 增
    def insert(self):
        pass

    # 删
    def delete(self):
        pass

    # 改
    def update(self):
        pass

    # def __del__(self):
    #     self.cursor.close()
    #     self.conn.close()


if __name__ == '__main__':
    sql_all = "select * from auth_group"

    sql_count = "select count(*) from auth_group"
    my_client = MyClient(
        host="127.0.0.1",
        username="root",
        password="123456",
        port=3306,
        database="mysite7"
    )
    records = my_client.select_one(sql_count)
    print(records)  # 表中可能无数据情况

    for i in range(records[0]):
        print(f"\033[1;40;32m{i}\033[0m")
        sql_one = "select * from auth_group limit %s,1" % i
        result = my_client.select_one(sql_one)
        print(result)
    SQL = "select * from information_schema.tables"
    table_names = my_client.select_all(SQL)
    print(table_names)