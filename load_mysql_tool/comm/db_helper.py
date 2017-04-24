#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 db_helper.py
# VERSION: 	 1.0
# CREATED: 	 2016-01-14 09:50
# AUTHOR: 	 xuexiang
# DESCRIPTION:   数据入库类
#
# HISTORY:
#*************************************************************

import MySQLdb


class db_helper_class:

    def __init__(self, db_conf0):
        self.db = MySQLdb.connect(
            host=db_conf0.db_host,
            port=db_conf0.db_port,
            user=db_conf0.db_user,
            passwd=db_conf0.db_passwd,
            db=db_conf0.db_name,
            charset="utf8")
        self.cursor = self.db.cursor(cursorclass=MySQLdb.cursors.DictCursor)

    def __del__(self):
        self.db.close()

    #**********************************************************************
    # 描  述： 数据库查询操作
    #
    # 参  数： sql, 查询语句
    #
    # 返回值： 返回一个元组，包含受影响的行数、及fetchall()迭代器
    # 修  改：
    #**********************************************************************
    def exe_search(self, sql):
        # 受影响的行数
        line_cnt = self.cursor.execute(sql)
        return (line_cnt, self.cursor.fetchall())

    #**********************************************************************
    # 描  述： 数据库insert插入操作
    #
    # 参  数： sql, 插入格式部分
    # 参  数： vals, 插入值元组
    #
    # 返回值： 空
    # 修  改：
    #**********************************************************************
    def exe_insert(self, sql, vals):
        self.cursor.execute(sql, vals)
        self.db.commit()

    #**********************************************************************
    # 描  述： update操作
    #
    # 参  数： sql, 查询语句
    #
    # 返回值： 空
    # 修  改：
    #**********************************************************************
    def exe_update(self, sql):
        self.cursor.execute(sql)
        self.db.commit()

    #**********************************************************************
    # 描  述： 获取select count计数值
    #
    # 参  数： sql, sql语句
    #
    # 返回值： 计数值
    # 修  改：
    #**********************************************************************
    def get_count(self, sql):
        ret_count = 0

        try:
            line_cnt = self.cursor.execute(sql)
            if line_cnt >= 0:
                ret_count = self.cursor.fetchall()[0].popitem()[1]
        except:
            pass

        return ret_count

    def get_cursor(self):
        return self.cursor
