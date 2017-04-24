#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 db_helper.py
# VERSION: 	 1.0
# CREATED: 	 2016-01-14 09:50
# AUTHOR: 	 xuexiang
# DESCRIPTION:   SQLserver操作类
#
# HISTORY:
#*************************************************************

import pymssql


class sqlser_helper_class:
    """
    对pymssql的简单封装
    pymssql库，该库到这里下载：http://www.lfd.uci.edu/~gohlke/pythonlibs/#pymssql
    使用该库时，需要在Sql Server Configuration Manager里面将TCP/IP协议开启

    用法：

    """

    def __init__(self, db_conf0):
        """
        得到连接信息conn.cursor()
        """
        self.conn = pymssql.connect(
            host=db_conf0.host,
            user=db_conf0.user,
            password=db_conf0.pwd,
            database=db_conf0.db,
            charset="utf8")
        self.cur = self.conn.cursor()

    def __del__(self):
        self.cur.close()
        self.conn.close()

    def ExecQuery(self,sql):
        """
        执行查询语句
        返回的是一个包含tuple的list，list的元素是记录行，tuple的元素是每行记录的字段
        """
        self.cur.execute(sql)
        resList = self.cur.fetchall()
        #查询完毕后必须关闭连接
        # self.conn.close()
        return resList

    def ExecNonQuery(self,sql):
        """
        执行非查询语句

        调用示例：
            cur = self.__GetConnect()
            cur.execute(sql)
            self.conn.commit()
            self.conn.close()
        """
        self.cur.execute(sql)
        self.conn.commit()
        # self.conn.close()
