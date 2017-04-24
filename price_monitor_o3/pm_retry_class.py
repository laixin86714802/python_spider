#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 pm_retry_class.py
# VERSION: 	 1.0
# CREATED: 	 2016-03-09 16:28
# AUTHOR: 	 xuexiang
# DESCRIPTION:
#
# HISTORY:
#*************************************************************
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import re
import time
import params_conf
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


class pm_retry_class():

    def __init__(self):
        self.db_oper = db_helper_class(conf.db_conf)
        # 分页大小
        self.page_size = 50
        # 读取偏移值
        self.r_offset = 0
        pass

    def __del__(self):
        pass

    def do_main(self):
        while True:
            # 只查询还没有被处理的
            sql = "select Id, comp_id, prod_id, url, retry_cnt from wrk_comweb_collect_retry \
                    where proc_state=0 limit %d offset %d" % (
                self.page_size, self.r_offset)
            (line_cnt, data_set) = self.db_oper.exe_search(sql)
            self.r_offset += self.page_size

            if line_cnt == 0:
                comm.PLog.Log("站点采集结束.")
                return

            for data_row in data_set:
                record_id = data_row["Id"]
                comp_id = data_row["comp_id"]
                prod_id = data_row["prod_id"]
                url = data_row["url"]
                retry_cnt = data_row["retry_cnt"]
                if retry_cnt is None:
                    retry_cnt = 0
                else:
                    retry_cnt = int(retry_cnt)

                comm.PLog.Log("========================================")
                comm.PLog.Log("comp_id=%s" % comp_id)
                comm.PLog.Log("prod_id=%s" % prod_id)
                comm.PLog.Log("url=%s" % url)
                comm.PLog.Log("retry_cnt=%s" % retry_cnt)

                # 解析
                self.parse_link(record_id, comp_id, prod_id, url, retry_cnt)

    # 使用此方法的前提条件：各站点的采集方法一样
    def parse_link(self, record_id, comp_id, prod_id, url, retry_cnt):
        # 产品价格
        fld_prod_price = 0.0

        try:
            comm.PLog.Log("%s 产品Id: %s" % (comp_id, prod_id))

            # 下载解析
            if comp_id == conf.class_conf.cls_zygw_jkw:
                fld_prod_price = pm_parse_class.parse_jkw(prod_id, url)
            elif comp_id == conf.class_conf.cls_zygw_yyw:
                fld_prod_price = pm_parse_class.parse_yyw(prod_id, url)
            elif comp_id == conf.class_conf.cls_zygw_kad:
                fld_prod_price = pm_parse_class.parse_kad(prod_id, url)
            elif comp_id == conf.class_conf.cls_zygw_kdl:
                fld_prod_price = pm_parse_class.parse_kdl(prod_id, url)
            elif comp_id == conf.class_conf.cls_zygw_jyw:
                fld_prod_price = pm_parse_class.parse_jyw(prod_id, url)
            elif comp_id == conf.class_conf.cls_zygw_lbx:
                fld_prod_price = pm_parse_class.parse_lbx(prod_id, url)
            elif comp_id == conf.class_conf.cls_zygw_ysk:
                fld_prod_price = pm_parse_class.parse_ysk(prod_id, url)
            elif comp_id == conf.class_conf.cls_zygw_yk:
                fld_prod_price = pm_parse_class.parse_yk(prod_id, url)
            elif comp_id == conf.class_conf.cls_zygw_kzj:
                fld_prod_price = pm_parse_class.parse_kzj(prod_id, url)
        except MyHttpDownFailed as ex:
            comm.PLog.Log("下载异常!")
        except MyHttpParseFailed as ex:
            comm.PLog.Log("解析异常!")
        except:
            comm.PLog.Log("其它异常!")
        finally:
            if fld_prod_price != 0:
                # 入库
                self.load_to_db(comp_id, prod_id, fld_prod_price)
                sql = "update wrk_comweb_collect_retry set proc_state=1 where id=%s" % (
                    record_id)
                self.db_oper.exe_update(sql)
            else:
                # 更新重试次数
                sql = "update wrk_comweb_collect_retry set retry_cnt=%s where id=%s" % (
                    retry_cnt + 1, record_id)
                self.db_oper.exe_update(sql)

    #**********************************************************************
    # 描  述： 价格信息入库
    #
    # 参  数： fld_prod_id, 产品id
    # 参  数： fld_prod_price, 价格
    #
    # 返回值： 空
    # 修  改：
    #**********************************************************************
    def load_to_db(self, comp_id, fld_prod_id, fld_prod_price):
        fld_inserttime = time.strftime("%Y-%m-%d %H:%M:%S")
        sql = "insert into wrk_comweb_hour_price(comp_id, prod_id, price, insert_time) \
                values(%s, %s, %s, %s)"

        value = (comp_id,
                 fld_prod_id,
                 fld_prod_price,
                 fld_inserttime)
        self.db_oper.exe_insert(sql, value)
        comm.PLog.Log("入库完成")
