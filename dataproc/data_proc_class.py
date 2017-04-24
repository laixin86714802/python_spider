#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 data_proc_class.py
# VERSION: 	 1.0
# CREATED: 	 2016-02-26 14:41
# AUTHOR: 	 xuexiang
# DESCRIPTION:
#
# HISTORY:
#*************************************************************
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import comm.PLog
import comm.requests_pkg
import conf.app_conf
import conf.class_conf
import conf.db_conf
from comm.db_helper import db_helper_class
import comm.job_report
from comm.JobSta import JobSta
from comm.MyHttpDownFailed import MyHttpDownFailed
from comm.MyHttpParseFailed import MyHttpParseFailed
import math


class data_proc_class():

    def __init__(self):
        self.db_oper = db_helper_class(conf.db_conf)
        # 分页大小
        self.page_size = 100
        # 读取偏移值
        self.r_offset = 0

        self.curr_prog = 0
        pass

    def __del__(self):
        pass

    def do_main(self):
        # 健客
        self.proc_one_com(100000)
        self.proc_one_com(100001)
        self.proc_one_com(100002)
        self.proc_one_com(100003)
        self.proc_one_com(100004)
        self.proc_one_com(100005)
        self.proc_one_com(100006)
        self.proc_one_com(100007)
        self.proc_one_com(100008)

        #self.proc_one_com_old_price_bug(100000)
        #self.proc_one_com_old_price_bug(100001)
        #self.proc_one_com_old_price_bug(100002)
        #self.proc_one_com_old_price_bug(100003)
        #self.proc_one_com_old_price_bug(100004)
        #self.proc_one_com_old_price_bug(100005)
        #self.proc_one_com_old_price_bug(100006)
        #self.proc_one_com_old_price_bug(100007)
        #self.proc_one_com_old_price_bug(100008)

        # 系统生命周期只需执行一次
        #self.proc_one_com_reverse(100000)
        #self.proc_one_com_reverse(100001)
        #self.proc_one_com_reverse(100002)
        #self.proc_one_com_reverse(100003)
        #self.proc_one_com_reverse(100004)
        #self.proc_one_com_reverse(100005)
        #self.proc_one_com_reverse(100006)
        #self.proc_one_com_reverse(100007)
        #self.proc_one_com_reverse(100008)

        #self.proc_break_data_recover(100000)
        #self.proc_break_data_recover(100001)
        #self.proc_break_data_recover(100002)
        #self.proc_break_data_recover(100003)
        #self.proc_break_data_recover(100004)
        #self.proc_break_data_recover(100005)
        #self.proc_break_data_recover(100006)
        #self.proc_break_data_recover(100007)
        #self.proc_break_data_recover(100008)
        pass

    def proc_one_com(self, comp_id):
        self.r_offset = 0
        self.curr_prog = 0
        comm.PLog.Log("开始处理")

        #target_tab = "tmp_day"
        #target_tab = "bk_wrk_comweb_day_price_20160226"
        target_tab = "wrk_comweb_day_price"

        # 获取总数量
        sql = "select count(*) from %s where comp_id=%s" % (target_tab, comp_id)
        all_cnt = self.db_oper.get_count(sql)
        comm.PLog.Log("总量: %s" % all_cnt)

        # 产品的当前价格
        old_prod_id = ""
        old_prod_price = 0

        while True:
            # 从数据库分页读取数据
            sql = "select id, prod_id, price, insert_time  \
                   from %s where comp_id=%s \
                   order by  prod_id, insert_time limit %d offset %d" % \
                (target_tab, comp_id, self.page_size, self.r_offset)
            (line_cnt, tbl_datas) = self.db_oper.exe_search(sql)

            self.r_offset += self.page_size

            if line_cnt == 0:
                comm.PLog.Log("处理结束.")
                return

            for row_data in tbl_datas:
                try:
                    curr_id = row_data["id"]
                    curr_prod_id = row_data["prod_id"]
                    curr_price = row_data["price"]

                    self.curr_prog += 1
                    comm.PLog.Log(
                        "curr_prog:%d/%d (%s)" %
                        (self.curr_prog, all_cnt, comp_id))
                    comm.PLog.Log(
                        "id=%s, prod=%s, curr_price: %s" %
                        (curr_id, curr_prod_id, curr_price))

                    if old_prod_id != curr_prod_id:
                        comm.PLog.Log(
                            "---------------------------------------")
                        comm.PLog.Log("开始处理新产品: %s " % curr_prod_id)
                        old_prod_id = curr_prod_id
                        old_prod_price = curr_price
                        continue

                    if (curr_price is None or curr_price ==
                            0) and old_prod_price != 0:
                        sql = "update %s set price=%s where id = %s" % (
                            target_tab, old_prod_price, curr_id)
                        self.db_oper.exe_update(sql)
                        comm.PLog.Log(
                            "\t>UP: comp_id=%s, prod_id=%s, give_price=%s" %
                            (comp_id, curr_prod_id, old_prod_price))

                    # 给old_price字段赋值
                    sql = "update %s set old_price=%s where id = %s" % (
                        target_tab, old_prod_price, curr_id)
                    self.db_oper.exe_update(sql)

                    if curr_price is not None and curr_price > 0 and curr_price != old_prod_price:
                        old_prod_price = curr_price
                        comm.PLog.Log("\t> 缓存Price:%s" % old_prod_price)

                except:
                    pass

    #**********************************************************************
    # 描  述： 处理之前因定时器bug造成的数据错误。
    #          （造成
    #
    # 返回值： 
    # 修  改： 
    #**********************************************************************
    def proc_one_com_old_price_bug(self, comp_id):
        self.r_offset = 0
        self.curr_prog = 0
        comm.PLog.Log("开始处理")

        #target_tab = "tmp_day"
        target_tab = "wrk_comweb_day_price"

        # 获取总数量
        sql = "select count(*) from %s where comp_id=%s" % (target_tab, comp_id)
        all_cnt = self.db_oper.get_count(sql)
        comm.PLog.Log("总量: %s" % all_cnt)

        # 产品的当前价格
        old_prod_id = ""
        old_prod_price = 0

        while True:
            # 从数据库分页读取数据
            sql = "select id, prod_id, price, insert_time  \
                   from %s where comp_id=%s \
                   order by  prod_id, insert_time limit %d offset %d" % \
                (target_tab, comp_id, self.page_size, self.r_offset)
            (line_cnt, tbl_datas) = self.db_oper.exe_search(sql)

            self.r_offset += self.page_size

            if line_cnt == 0:
                comm.PLog.Log("处理结束.")
                return

            for row_data in tbl_datas:
                try:
                    curr_id = row_data["id"]
                    curr_prod_id = row_data["prod_id"]
                    curr_price = row_data["price"]

                    self.curr_prog += 1
                    comm.PLog.Log(
                        "curr_prog:%d/%d (%s)" %
                        (self.curr_prog, all_cnt, comp_id))
                    comm.PLog.Log(
                        "id=%s, prod=%s, curr_price: %s" %
                        (curr_id, curr_prod_id, curr_price))

                    if old_prod_id != curr_prod_id:
                        comm.PLog.Log(
                            "---------------------------------------")
                        comm.PLog.Log("开始处理新产品: %s " % curr_prod_id)
                        old_prod_id = curr_prod_id
                        old_prod_price = curr_price
                        continue

                    if old_prod_price != 0:
                        sql = "update %s set old_price=%s where id = %s" % (
                            target_tab, old_prod_price, curr_id)
                        self.db_oper.exe_update(sql)
                        comm.PLog.Log(
                            "\t>UP: comp_id=%s, prod_id=%s, give_old_price=%s" %
                            (comp_id, curr_prod_id, old_prod_price))

                    if curr_price is not None and curr_price > 0:
                        old_prod_price = curr_price
                        comm.PLog.Log("\t> 缓存Price:%s" % old_prod_price)

                except:
                    pass

    #**********************************************************************
    # 描  述： 逆向赋值
    #          注：只给prie赋值，不能给old_price赋值
    #
    # 返回值：
    # 修  改：
    #**********************************************************************
    def proc_one_com_reverse(self, comp_id):
        self.r_offset = 0
        self.curr_prog = 0
        comm.PLog.Log("开始处理")

        #target_tab = "tmp_day"
        #target_tab = "bk_wrk_comweb_day_price_20160226"
        target_tab = "wrk_comweb_day_price"

        # 获取总数量
        sql = "select count(*) from %s where comp_id=%s" % (target_tab, comp_id)
        all_cnt = self.db_oper.get_count(sql)
        comm.PLog.Log("总量: %s" % all_cnt)

        # 产品的当前价格
        old_prod_id = ""
        old_prod_price = 0

        while True:
            # 从数据库分页读取数据
            sql = "select id, prod_id, price, insert_time  \
                   from %s where comp_id=%s \
                   order by  prod_id, insert_time desc limit %d offset %d" % \
                (target_tab, comp_id, self.page_size, self.r_offset)
            (line_cnt, tbl_datas) = self.db_oper.exe_search(sql)

            self.r_offset += self.page_size

            if line_cnt == 0:
                comm.PLog.Log("处理结束.")
                return

            for row_data in tbl_datas:
                try:
                    curr_id = row_data["id"]
                    curr_prod_id = row_data["prod_id"]
                    curr_price = row_data["price"]

                    self.curr_prog += 1
                    comm.PLog.Log(
                        "curr_prog:%d/%d (%s)" %
                        (self.curr_prog, all_cnt, comp_id))
                    comm.PLog.Log(
                        "id=%s, prod=%s, curr_price: %s" %
                        (curr_id, curr_prod_id, curr_price))

                    if old_prod_id != curr_prod_id:
                        comm.PLog.Log(
                            "---------------------------------------")
                        comm.PLog.Log("开始处理新产品: %s " % curr_prod_id)
                        old_prod_id = curr_prod_id
                        old_prod_price = curr_price
                        continue

                    if (curr_price is None or curr_price ==
                            0) and old_prod_price != 0:
                        sql = "update %s set price=%s where id = %s" % (
                            target_tab, old_prod_price, curr_id)
                        self.db_oper.exe_update(sql)
                        comm.PLog.Log(
                            "\t>UP: comp_id=%s, prod_id=%s, give_price=%s" %
                            (comp_id, curr_prod_id, old_prod_price))

                    if curr_price is not None and curr_price > 0 and curr_price != old_prod_price:
                        old_prod_price = curr_price
                        comm.PLog.Log("\t> 缓存Price:%s" % old_prod_price)

                except:
                    pass

    # 中断数据恢复
    def proc_break_data_recover(self, comp_id):
        self.r_offset = 0
        self.curr_prog = 0
        comm.PLog.Log("开始处理")

        #target_tab = "tmp_day"
        #target_tab = "bk_wrk_comweb_day_price_20160226"
        target_tab = "wrk_comweb_day_price"

        # 获取总数量
        sql = "select count(*) from %s where comp_id=%s" % (target_tab, comp_id)
        all_cnt = self.db_oper.get_count(sql)
        comm.PLog.Log("总量: %s" % all_cnt)

        # 产品的当前价格
        old_prod_id = ""
        old_id = ""
        old_did = 0

        while True:
            # 从数据库分页读取数据
            sql = " select id, prod_id, date_format(insert_time, '%%Y-%%m-%%d') as dat, \
                    cast((UNIX_TIMESTAMP(date_format(insert_time, '%%Y-%%m-%%d')) -  1450972800) /86400 as SIGNED )  as did \
                    from %s  where comp_id=%s \
                    order by  prod_id, insert_time limit %d offset %d" % \
                (target_tab, comp_id, self.page_size, self.r_offset)
            (line_cnt, tbl_datas) = self.db_oper.exe_search(sql)

            self.r_offset += self.page_size

            if line_cnt == 0:
                comm.PLog.Log("处理结束.")
                return

            for row_data in tbl_datas:
                try:
                    curr_id = row_data["id"]
                    curr_prod_id = row_data["prod_id"]
                    curr_date = row_data["dat"]
                    curr_did = row_data["did"]

                    self.curr_prog += 1
                    comm.PLog.Log(
                        "curr_prog:%d/%d (%s)" %
                        (self.curr_prog, all_cnt, comp_id))
                    comm.PLog.Log(
                        "id=%s, prod=%s" %
                        (curr_id, curr_prod_id))
                    comm.PLog.Log(
                        "curr_date=%s, curr_did=%s" %
                        (curr_date, curr_did))

                    if old_prod_id != curr_prod_id:
                        comm.PLog.Log(
                            "---------------------------------------")
                        comm.PLog.Log("开始处理新产品: %s " % curr_prod_id)
                        old_id = curr_id
                        old_prod_id = curr_prod_id
                        # 日期序号
                        old_did = curr_did
                        continue

                    # 被填范围[old_did+1, curr_did)
                    add_num = 1
                    for k in range(old_did + 1, curr_did):
                        comm.PLog.Log("==========")
                        comm.PLog.Log(
                            "prod_id=%s, insert did=%d" %
                            (curr_prod_id, k))
                        sql = "insert into %s(comp_id, prod_id, prod_name, \
                               old_price, price, insert_time, remark) \
                               select comp_id, prod_id, prod_name, old_price, price, \
                               DATE_ADD(insert_time,INTERVAL %d DAY), remark \
                               from %s where id = %d" % \
                            ("tmp_day_cache", add_num, target_tab, old_id)
                        self.db_oper.exe_update(sql)
                        add_num = add_num + 1

                    old_id = curr_id
                    old_did = curr_did
                except:
                    pass
