# !/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:lupengliang
import logging
import os
import re
import time

import pymysql
from tqdm import tqdm

from base.excel import Excel
from base.readCofing import myUsername
from base.readCofing import myPassword
from base.readCofing import myIp
from base.readCofing import myPort
from base.readCofing import myDatabase
from base.readCofing import obUsername
from base.readCofing import obPassword
from base.readCofing import obIp
from base.readCofing import obPort
from base.readCofing import obDatabase
from base.sqlClient import MyClient


class Run:

    def __init__(self):
        pass

    # 获取单个数据库的中表名列表
    @classmethod
    def get_database_tables(cls, client, database):
        try:
            SQL = f"select TABLE_NAME from information_schema.tables where table_schema = '{database}'"
            result = re.findall("\('(.*?)',\)", str(client.select_all(SQL)))
        except TypeError:
            result = []
        return result

    # 获取单个数据表的数据记录数
    @classmethod
    def get_table_count(cls, client, table_name):
        try:
            SQL = f"select count(*) from {table_name}"
            table_rows = client.select_all(SQL)[0][0]
        except TypeError:
            table_rows = 0
        return table_rows

    # 获取单个数据表的所有记录
    @classmethod
    def get_table_all(cls, client, table_name):
        SQL = f"select * from {table_name}"
        table_data = client.select_all(SQL)
        return table_data

    # 获取单个数据表的下一条记录
    @classmethod
    def get_table_one(cls, client, table_name, i):
        """
        :param client:
        :param table_name:
        :param i: for i in range(表列表): i=0 表示第一行记录
        :return:
        """
        SQL = f"select * from {table_name} limit {i}, 1"
        next_one_data = client.select_all(SQL)
        return next_one_data

    # 创建Excel结果集
    @classmethod
    def create_compare_result(cls, database):
        """
        :param database: 数据库列表
        :return:
        """
        execl = Excel("result.xlsx")
        wb = execl.create_excel("result.xlsx", sheet_name="结果总览")
        ws = wb["结果总览"]
        execl.write_by_append(ws, ["数据库", "表", "数据是否一致"])
        for database_name in database:
            wb = execl.create_sheet(wb, database_name)
            ws = wb[database_name]
            execl.write_by_append(ws, ["数据库", "表", "数据(未去重)"])
        execl.save_excel(wb)

    # 比较数据库配置的数量
    @classmethod
    def compare_database_same(cls):
        """
        mysql-dbrisk: mysql 没有配置 dbrisk
        ob-dbrisk: ob 没有配置 dbrisk
        :return:
        """
        execl = Excel("result.xlsx")
        wb = execl.load_excel()
        ws = wb["结果总览"]
        if len(obDatabase) != len(myDatabase):
            logging.error("please config database count to same.")
            for database_name in obDatabase:
                if database_name not in myDatabase:
                    logging.error(f"mysql server no database {database_name}.")
                    execl.write_by_append(ws, ["mysql--"+database_name, "-", "-"])

            for database_name in myDatabase:
                if database_name not in obDatabase:
                    logging.error(f"ob server no database {database_name}.")
                    execl.write_by_append(ws, ["ob--" + database_name, "-", "-"])
        execl.save_excel(wb)

    # 比较单个数据库中表的数量
    @classmethod
    def compare_database_table_count(cls, ob_client, my_client, database):
        execl = Excel("result.xlsx")
        wb = execl.load_excel()
        ws = wb["结果总览"]
        my_tables = Run.get_database_tables(my_client, database)
        ob_tables = Run.get_database_tables(ob_client, database)
        if len(my_tables) != len(ob_tables):
            for table in ob_tables:
                if table not in my_tables:
                    execl.write_by_append(ws, ["mysql--" + database, table, "-"])

            for table in my_tables:
                if table not in ob_tables:
                    execl.write_by_append(ws, ["ob--" + database, table, "-"])
        execl.save_excel(wb)

    # 比较单个表的数据记录量
    @classmethod
    def compare_table_data_count(cls, ob_client, my_client, database, table_name):
        execl = Excel("result.xlsx")
        wb = execl.load_excel()
        my_table_rows = Run.get_table_count(my_client, table_name)
        ob_table_rows = Run.get_table_count(ob_client, table_name)
        if my_table_rows != ob_table_rows:
            ws = wb["结果总览"]
            execl.write_by_append(ws, [database, table_name, "数量记录不同"])
        execl.save_excel(wb)

    # 比较单个表中的不同数据
    @classmethod
    def compare_table_data(cls, ob_client, my_client, database, table_name):
        """
        如果tabel1没有table2的数据，table2没有table1的数据，暂时没有做Excel结果去重
        :param ob_client:
        :param my_client:
        :param database:
        :param table_name:
        :return:
        """
        execl = Excel("result.xlsx")
        wb = execl.load_excel()
        my_table_rows = Run.get_table_count(my_client, table_name)
        ob_table_rows = Run.get_table_count(ob_client, table_name)
        for i in range(my_table_rows):
            my_data_one = Run.get_table_one(my_client, table_name, i)
            ob_data_one = Run.get_table_one(ob_client, table_name, i)
            if my_data_one != ob_data_one:
                ws = wb[database]
                execl.write_by_append(ws, ["mysql -- " + database, table_name, str(my_data_one)])
                execl.write_by_append(ws, ["ob -- " + database, table_name, str(ob_data_one)])
                ws = wb["结果总览"]
                execl.write_by_append(ws, [database, table_name, "否"])
        for j in range(ob_table_rows):
            my_data_one = Run.get_table_one(my_client, table_name, j)
            ob_data_one = Run.get_table_one(ob_client, table_name, j)
            if my_data_one != ob_data_one:
                ws = wb[database]
                execl.write_by_append(ws, ["mysql -- " + database, table_name, str(my_data_one)])
                execl.write_by_append(ws, ["ob -- " + database, table_name, str(ob_data_one)])
                ws = wb["结果总览"]
                execl.write_by_append(ws, [database, table_name, "否"])
        execl.save_excel(wb)


if __name__ == '__main__':
    logging.basicConfig(level="ERROR", format='%(asctime)s [%(levelname)s]: %(message)s')
    try:
        os.remove("./result.xlsx")
    except Exception:
        pass
    Run.create_compare_result(myDatabase)  # 比较数据库的配置个数
    time.sleep(2)
    Run.compare_database_same()
    for database in myDatabase:
        try:
            my_client = MyClient(host=myIp, username=myUsername, password=myPassword, port=myPort, database=database)
            ob_client = MyClient(host=obIp, username=obUsername, password=obPassword, port=obPort, database=database)
            my_tables = Run.get_database_tables(my_client, database)
            ob_tables = Run.get_database_tables(ob_client, database)
            Run.compare_database_table_count(ob_client, my_client, database)  # 记录ob与mysql数据库缺少的数据表
            for table_name in tqdm(ob_tables):
                tqdm(ob_tables).set_description(f"{database}  %s " % table_name)
                Run.compare_table_data_count(ob_client, my_client, database, table_name)  # 比较数据表中的数据记录数一致致
                Run.compare_table_data(ob_client, my_client, database, table_name)  # 记录表中不一样的数据记录

            for table_name in tqdm(my_tables):
                tqdm(ob_tables).set_description(f"{database}  %s " % table_name)
                Run.compare_table_data_count(ob_client, my_client, database, table_name)
                Run.compare_table_data(ob_client, my_client, database, table_name)
        except pymysql.err.OperationalError:
            logging.critical(f'1049, "Unknown database {database}"')
            continue
