#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 pm_collect_class.py
# VERSION: 	 1.0
# CREATED: 	 2016-02-22 13:17
# AUTHOR: 	 xuexiang
# DESCRIPTION:   自主官网数据采集
#
# HISTORY:
#           WLT 2016-03-09 添加如下功能点：
#               （1）处理数据前，先加载异常监控表到字典。
#　                 　若取到数据，且存在于异常监控表，则从异常监控表中移除，并记录到历史表（再次上架）
#                     若没有取到数据，且存在于异常监控表，则不处理。 且这种数据，在最终的定时任务中需要清除。
#                     若没有取到数据，且不存在于异常监控表，则需要周期性重试。 尽可能取到价格信息。
#
#*************************************************************

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import re
import time
import params_conf
import traceback
import comm.PLog
import comm.stone_funs
import comm.requests_pkg
import comm.job_report

import conf.app_conf
import conf.class_conf
import conf.db_conf
from comm.db_helper import db_helper_class
from comm.MyHttpDownFailed import MyHttpDownFailed
from comm.MyHttpParseFailed import MyHttpParseFailed
from comm.JobSta import JobSta
from pm_parse_class import pm_parse_class


class pm_collect_class():

    def __init__(self):
        self.db_oper = db_helper_class(conf.db_conf)
        # 分页大小
        self.page_size = 20
        # 读取偏移值
        self.r_offset = 0
        self.app_id = conf.app_conf.app_zygw_collect_id

    def __del__(self):
        pass

    def do_main(self, class_id, web_name):
        self.class_id = class_id
        self.web_name = web_name
        self.job_id = "%s_%s_%s" % (time.strftime(
            'T%Y%m%d%H%M'), self.app_id, self.class_id)
        self.job_stat = JobSta()

        # 加载当前商家异常监控set集合
        sql = "select prod_id from wrk_comweb_except_prod where comp_id=%d" % (
            self.class_id)
        (line_cnt, data_view) = self.db_oper.exe_search(sql)
        comm.PLog.Log("当前异常监控记录数=%d" % line_cnt)

        self.except_prods_set = set()
        for data_row in data_view:
            prod_id = data_row["prod_id"]
            self.except_prods_set.add(prod_id)

        if self.class_id == conf.class_conf.cls_zygw_jkw:
            self.do_jk_collect_frame()
        else:
            self.do_comp_collect_frame()

    #**********************************************************************
    # 描  述： 键客采集框架
    #
    # 返回值： 空
    # 修  改：
    #**********************************************************************
    def do_jk_collect_frame(self):
        comm.PLog.Log("开始处理%s." % self.web_name)

        # 获取总任务量
        sql = "select  count(distinct jk_prod_id) from bas_comweb_url"
        self.job_stat.all_task_count = self.db_oper.get_count(sql)
        comm.PLog.Log("总任务数:%d" % self.job_stat.all_task_count)
        # 初始化Job Report
        comm.job_report.report_start(self.app_id, self.class_id, self.job_id,
                                     self.job_stat.all_task_count, self.db_oper)
        curr_counter = 0

        while True:
            sql = "select distinct jk_prod_id, jk_prod_name from bas_comweb_url  limit %d offset %d" % (
                self.page_size, self.r_offset)
            (line_cnt, data_set) = self.db_oper.exe_search(sql)
            self.r_offset += self.page_size

            if line_cnt == 0:
                comm.PLog.Log("站点采集结束.")
                return

            for data_row in data_set:
                print "=================================================="
                curr_counter += 1
                comm.PLog.Log("采集进度:%d/%d, 下载失败:%d, 解析失败:%d" %
                              (curr_counter, self.job_stat.all_task_count,
                               self.job_stat.down_failed_count, self.job_stat.parse_failed_count))

                # 产品ID
                fld_prod_id = data_row["jk_prod_id"]
                # 产品价格
                fld_prod_price = 0.0

                try:
                    comm.PLog.Log("%s 产品Id: %s" %
                                  (self.web_name, data_row['jk_prod_id']))
                    url = "http://m.jianke.com/product/%s.html" % data_row[
                        'jk_prod_id']
                    fld_prod_price = pm_parse_class.parse_jkw(fld_prod_id, url)
                    comm.PLog.Log("price=%.2f" % fld_prod_price)

                    self.job_stat.down_ok_count += 1
                # except MyHttpDownFailed as ex:
                #     comm.PLog.Log("下载异常!")
                #     self.job_stat.down_failed_count += 1
                # except MyHttpParseFailed as ex:
                #     comm.PLog.Log("解析异常!")
                #     self.job_stat.parse_failed_count += 1
                # except:
                #     comm.PLog.Log("其它异常!")
                #     self.job_stat.other_failed_count += 1
                except:
                    print traceback.format_exc()
                finally:
                    # 异常数据处理
                    self.price_except_proc(fld_prod_id, fld_prod_price, url)
                    # 入库
                    self.load_to_db(fld_prod_id, fld_prod_price)

        # 写统计报告
        self.report_complate()

    #**********************************************************************
    # 描  述： 竞争对手采集框架
    #
    # 返回值： 空
    # 修  改：
    #**********************************************************************
    def do_comp_collect_frame(self):
        comm.PLog.Log("开始处理%s." % self.web_name)

        # 获取总任务量
        sql = "select count(distinct comp_prod_id) from bas_comweb_url where comp_id='%s'" % self.class_id
        self.job_stat.all_task_count = self.db_oper.get_count(sql)
        comm.PLog.Log("总任务数:%d" % self.job_stat.all_task_count)
        # 初始化Job Report
        comm.job_report.report_start(self.app_id, self.class_id, self.job_id,
                                     self.job_stat.all_task_count, self.db_oper)

        curr_counter = 0

        while True:
            sql = "select distinct comp_prod_id, url from bas_comweb_url where comp_id='%s' \
                   limit %d offset %d" % (self.class_id, self.page_size, self.r_offset)
            (line_cnt, data_set) = self.db_oper.exe_search(sql)
            self.r_offset += self.page_size

            if line_cnt == 0:
                comm.PLog.Log("站点采集结束.")
                return

            for data_row in data_set:
                print "=================================================="
                curr_counter += 1
                comm.PLog.Log("采集进度:%d/%d, 下载失败:%d, 解析失败:%d" %
                              (curr_counter, self.job_stat.all_task_count,
                               self.job_stat.down_failed_count, self.job_stat.parse_failed_count))

                # 产品ID
                fld_prod_id = data_row["comp_prod_id"]
                # 产品价格
                fld_prod_price = 0.0

                try:
                    comm.PLog.Log("%s 产品Id: %s" %
                                  (self.web_name, data_row['comp_prod_id']))
                    prod_id = data_row["comp_prod_id"]
                    url = data_row['url']

                    # 下载解析
                    if self.class_id == conf.class_conf.cls_zygw_yyw:
                        fld_prod_price = pm_parse_class.parse_yyw(prod_id, url)
                    elif self.class_id == conf.class_conf.cls_zygw_kad:
                        fld_prod_price = pm_parse_class.parse_kad(prod_id, url)
                    elif self.class_id == conf.class_conf.cls_zygw_kdl:
                        fld_prod_price = pm_parse_class.parse_kdl(prod_id, url)
                    elif self.class_id == conf.class_conf.cls_zygw_jyw:
                        fld_prod_price = pm_parse_class.parse_jyw(prod_id, url)
                    elif self.class_id == conf.class_conf.cls_zygw_lbx:
                        fld_prod_price = pm_parse_class.parse_lbx(prod_id, url)
                    elif self.class_id == conf.class_conf.cls_zygw_ysk:
                        fld_prod_price = pm_parse_class.parse_ysk(prod_id, url)
                    elif self.class_id == conf.class_conf.cls_zygw_yk:
                        fld_prod_price = pm_parse_class.parse_yk(prod_id, url)
                    elif self.class_id == conf.class_conf.cls_zygw_kzj:
                        fld_prod_price = pm_parse_class.parse_kzj(prod_id, url)

                    comm.PLog.Log("price=%.2f" % fld_prod_price)

                    self.job_stat.down_ok_count += 1
                # except MyHttpDownFailed as ex:
                #     comm.PLog.Log("下载异常!")
                #     self.job_stat.down_failed_count += 1
                # except MyHttpParseFailed as ex:
                #     comm.PLog.Log("解析异常!")
                #     self.job_stat.parse_failed_count += 1
                # except:
                #     comm.PLog.Log("其它异常!")
                #     self.job_stat.other_failed_count += 1
                except:
                    print traceback.format_exc()
                finally:
                    # 异常数据处理
                    self.price_except_proc(prod_id, fld_prod_price, url)
                    # 入库
                    self.load_to_db(fld_prod_id, fld_prod_price)

        # 写统计报告
        self.report_complate()

        pass

    #**********************************************************************
    # 描  述： 价格异常监控处理
    #　        若取到数据，且存在于异常监控表，则从异常监控表中移除，并记录到历史表（再次上架）
    #          若没有取到数据，且存在于异常监控表，则不处理。 且这种数据，在最终的定时任务中需要清除。
    #          若没有取到数据，且不存在于异常监控表，则需要周期性重试。 尽可能取到价格信息。
    #
    # 参  数： prod_id, 产品Id
    # 参  数： price, 价格信息
    # 参  数： url, 地址信息
    #
    # 返回值： 空
    # 修  改：
    #**********************************************************************
    def price_except_proc(self, prod_id, price, url):
        if price > 0:
            if prod_id in self.except_prods_set:
                comm.PLog.Log("再次上线!")
                # 插入到历史表
                sql = "insert into wrk_comweb_except_history(comp_id, prod_id, exp_cause, exp_date) \
                        values(%s, %s, %s, %s)"
                vals = (self.class_id, prod_id, 1, time.strftime("%Y-%m-%d"))
                self.db_oper.exe_insert(sql, vals)
                # 从当前表删除
                sql = "delete from wrk_comweb_except_prod where comp_id=%s and prod_id=%s" \
                    % (self.class_id, prod_id)
                self.db_oper.exe_search(sql)
        else:
            if prod_id in self.except_prods_set:
                comm.PLog.Log("下架保持!")
                # 不做任何处理
                pass
            else:
                comm.PLog.Log("需要重试!")
                # 写重试表
                sql = "insert into wrk_comweb_collect_retry(comp_id, prod_id, url) values(%s, %s, %s)"
                vals = (self.class_id, prod_id, url)
                self.db_oper.exe_insert(sql, vals)

    #**********************************************************************
    # 描  述： 价格信息入库
    #
    # 参  数： fld_prod_id, 产品id
    # 参  数： fld_prod_price, 价格
    #
    # 返回值： 空
    # 修  改：
    #**********************************************************************
    def load_to_db(self, fld_prod_id, fld_prod_price):
        fld_inserttime = time.strftime("%Y-%m-%d %H:%M:%S")
        sql = "insert into wrk_comweb_hour_price(comp_id, prod_id, price, insert_time) \
                values(%s, %s, %s, %s)"

        value = (self.class_id,
                 fld_prod_id,
                 fld_prod_price,
                 fld_inserttime)
        self.db_oper.exe_insert(sql, value)
        comm.PLog.Log("入库完成")

    #**********************************************************************
    # 描  述：任务完成报告
    #
    # 返回值：空
    # 修  改：
    #**********************************************************************
    def report_complate(self):
        comm.job_report.report_finish(
            self.job_id, self.job_stat, self.db_oper, self.web_name)
