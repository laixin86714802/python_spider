#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 pm_collect_class.py
# VERSION: 	 1.0
# CREATED: 	 2016-07-22 13:17
# AUTHOR: 	 xuexiang
# DESCRIPTION:   360好药网数据采集
#
# HISTORY:
#           WLT 2016-03-09 添加如下功能点：
#               （1）处理数据前，先加载异常保持表到字典。
#　                 　若取到数据，且存在于异常保持表，则从异常保持表中移除
#                     若没有取到数据，且存在于异常保持表，则不处理。 且这种数据，在最终的定时任务中需要清除。
#                     若没有取到数据，且不存在于异常保持表，则需要周期性重试。 尽可能取到价格信息。
#
#*************************************************************

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import re
import time
import spynner
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


class pm_360_collect_class():

    #**********************************************************************
    # 描  述： 构造函数
    #
    # 返回值：
    # 修  改：
    #**********************************************************************
    def __init__(self):
        self.m_browser = spynner.Browser()
        self.m_browser.hide()

        # 数据库对象
        self.db_oper = db_helper_class(conf.db_conf)
        # 分页大小
        self.page_size = 20
        # 读取偏移值
        self.r_offset = 0

        self.app_id = conf.app_conf.app_360haoyao_id
        self.class_id = conf.class_conf.class_360haoyao_all

    #**********************************************************************
    # 描  述： 析构函数
    #
    # 返回值：
    # 修  改：
    #**********************************************************************
    def __del__(self):
        pass

    #**********************************************************************
    # 描  述： 清理会话
    #
    # 返回值：
    # 修  改：
    #**********************************************************************
    def clear_session(self):
        self.r_offset = 0

    #**********************************************************************
    # 描  述： 会话初始化
    #
    # 返回值：
    # 修  改：
    #**********************************************************************
    def session_start(self):
        self.job_id = "%s_%s_%s" % (time.strftime(
            'T%Y%m%d%H%M'), self.app_id, self.class_id)
        self.job_stat = JobSta()

        # 清空重试表
        sql = "delete from wrk_360_except_now"
        self.db_oper.exe_update(sql)

        # 加载异常保持记录
        sql = "select distinct prod_id from wrk_360_except_keep"
        (line_cnt, data_view) = self.db_oper.exe_search(sql)
        comm.PLog.Log("当前异常保持记录数=%d" % line_cnt)

        self.except_prods_set = set()
        for data_row in data_view:
            prod_id = data_row["prod_id"]
            self.except_prods_set.add(prod_id)

        # 获取总任务量(健客)
        sql = "select count(distinct jk_360_pid) from bas_360_products "
        self.job_stat.all_task_count = self.db_oper.get_count(sql)

        # 获取总任务量(竞争对手)
        sql = "select count(distinct comp_360_pid) from bas_360_products"
        self.job_stat.all_task_count += self.db_oper.get_count(sql)

        # 初始化Job Report
        comm.PLog.Log("总任务数:%d" % self.job_stat.all_task_count)
        comm.job_report.report_start(self.app_id, self.class_id, self.job_id,
                                     self.job_stat.all_task_count, self.db_oper)

        self.curr_counter = 0

    #**********************************************************************
    # 描  述： 会话结束
    #
    # 返回值：
    # 修  改：
    #**********************************************************************
    def session_finish(self):
        # 写统计报告
        self.report_complate()

    #**********************************************************************
    # 描  述： 主处理函数
    #
    # 返回值：
    # 修  改：
    #**********************************************************************
    def do_main(self):

        self.session_start()

        try:
            # 采集键客店铺数据
            self.clear_session()
            self.do_collect_jk_shop()

            # 采集对手店铺数据
            self.clear_session()
            self.do_collect_comp_shop()
        except:
            pass

        self.session_finish()

    #**********************************************************************
    # 描  述： 键客采集框架
    #
    # 返回值： 空
    # 修  改：
    #**********************************************************************
    def do_collect_jk_shop(self):
        self.web_name = "键客店铺"
        comm.PLog.Log("开始处理%s." % self.web_name)

        while True:
            sql = "select distinct jk_360_pid from bas_360_products limit %d offset %d" % (
                self.page_size, self.r_offset)
            (line_cnt, data_set) = self.db_oper.exe_search(sql)
            self.r_offset += self.page_size

            if line_cnt == 0:
                comm.PLog.Log("键客店铺采集结束.")
                break

            for data_row in data_set:
                print "=================================================="
                self.curr_counter += 1
                comm.PLog.Log("采集进度:%d/%d, 下载失败:%d, 解析失败:%d" %
                              (self.curr_counter, self.job_stat.all_task_count,
                               self.job_stat.down_failed_count, self.job_stat.parse_failed_count))

                # 产品ID
                fld_prod_id = data_row["jk_360_pid"]

                if self.is_exist(fld_prod_id):
                    comm.PLog.Log("已经存在，不重复采集!");
                    continue;

                # 产品价格
                fld_prod_price = None
                fld_image_name = ""
                jk_shop_id = "100000"
                html_content = ""
                #产品销量
                fld_prod_num = None
                
                try:
                    comm.PLog.Log("%s 产品Id: %s" %
                                  (self.web_name, data_row['jk_360_pid']))
                    url = "http://www.360haoyao.com/item/%s.html" % data_row[
                        'jk_360_pid']
                    (fld_prod_num, fld_prod_price, fld_image_name, html_content) = self.down_page(
                        fld_prod_id, url)

                    if fld_prod_price == None:
                        raise MyHttpParseFailed();
                    else:
                        self.job_stat.down_ok_count += 1

                        # 先请求图片
                        self.request_thumb_image(fld_prod_id, fld_image_name)

                        # 入库
                        self.load_to_db(jk_shop_id, fld_prod_id, fld_prod_price,fld_prod_num)

                except MyHttpDownFailed as ex:
                    comm.PLog.Log("下载异常!")
                    self.job_stat.down_failed_count += 1
                except MyHttpParseFailed as ex:
                    comm.PLog.Log("解析异常!")
                    self.job_stat.parse_failed_count += 1
                except:
                    comm.PLog.Log("其它异常!")
                    self.job_stat.other_failed_count += 1
                finally:
                    # 异常数据处理
                    self.price_except_proc( jk_shop_id, fld_prod_id, fld_prod_price, url, html_content)

    def is_exist(self, product_id):
        # 当前日期
        fld_now_date = time.strftime(
            '%Y-%m-%d', time.localtime(int(time.time())))

        # 查询是否已经存在
        sql = "select Id from wrk_360_products_price where prod_id='%s' and insert_time like '%s%%'" % (
            product_id, fld_now_date)
        (line_cnt, tbl_datas) = self.db_oper.exe_search(sql)
        if line_cnt > 0: 
            return True;

        return False;

    #**********************************************************************
    # 描  述： 竞争对手采集框架
    #
    # 返回值： 空
    # 修  改：
    #**********************************************************************
    def do_collect_comp_shop(self):
        self.web_name = "所有对手店铺"
        comm.PLog.Log("开始处理%s." % self.web_name)

        while True:
            sql = "select comp_id, comp_360_pid from bas_360_products  \
                   limit %d offset %d" % (self.page_size, self.r_offset)
            (line_cnt, data_set) = self.db_oper.exe_search(sql)
            self.r_offset += self.page_size

            if line_cnt == 0:
                comm.PLog.Log("对手站点采集结束.")
                break

            for data_row in data_set:
                print "=================================================="
                self.curr_counter += 1
                comm.PLog.Log("采集进度:%d/%d, 下载失败:%d, 解析失败:%d" %
                              (self.curr_counter, self.job_stat.all_task_count,
                               self.job_stat.down_failed_count, self.job_stat.parse_failed_count))

                # 对手ID
                fld_comp_id = data_row["comp_id"]
                # 对手产品ID
                fld_prod_id = data_row["comp_360_pid"]

                if self.is_exist(fld_prod_id):
                    comm.PLog.Log("已经存在，不重复采集!");
                    continue;

                # 产品价格
                fld_prod_price = None
                html_content = ""
                # 产品销量
                fld_prod_num = None

                try:
                    comm.PLog.Log("%s 产品Id: %s" %
                                  (self.web_name, data_row['comp_360_pid']))
                    prod_id = data_row["comp_360_pid"]

                    url = "http://www.360haoyao.com/item/%s.html" % prod_id
                    (fld_prod_num, fld_prod_price, fld_image_name, html_content) = self.down_page(
                        fld_prod_id, url)

                    if fld_prod_price == None:
                        raise MyHttpParseFailed();
                    else:
                        # 入库
                        self.load_to_db(fld_comp_id, fld_prod_id, fld_prod_price, fld_prod_num)

                        self.job_stat.down_ok_count += 1

                except MyHttpDownFailed as ex:
                    comm.PLog.Log("下载异常!")
                    self.job_stat.down_failed_count += 1
                except MyHttpParseFailed as ex:
                    comm.PLog.Log("解析异常!")
                    self.job_stat.parse_failed_count += 1
                except:
                    comm.PLog.Log("其它异常!")
                    self.job_stat.other_failed_count += 1
                finally:
                    # 异常数据处理
                    self.price_except_proc(
                        fld_comp_id, prod_id, fld_prod_price, url, html_content)

    #**********************************************************************
    # 描  述：页面下载解析
    #
    # 参  数：product_id, 产品Id
    # 参  数：Url, 产品链接
    #
    # 返回值：
    # 修  改：
    #**********************************************************************
    def down_page(self, product_id, url):
        self.m_browser.load(url=url, load_timeout=120, tries=3)
        html_content = str(self.m_browser.html)

        comm.PLog.Log("Page下载完成")
        comm.PLog.TempLog("%s.log" % product_id, html_content)

        # 价格
        price = None
        re_price = re.search(
            r'''(?:价.*?</i><em>)(?P<sPrice>[\d\.]+)(?:</em>)''',
            html_content,
            re.S | re.I)
        if re_price is not None:
            price = re_price.group("sPrice")
            comm.PLog.Log("price=%s" % price)

        # 销量或预定数
        prod_num = None
        re_prod_num = re.search(
            r'''(?:saleText.*?)(?P<sProdNum>[\d]+)(?:</span>)''',
            html_content,
            re.S | re.I)
        if re_prod_num is not None:
            prod_num = re_prod_num.group("sProdNum")
            comm.PLog.Log("prod_num=%s" % prod_num)

        # 图片地址
        image_name = ""
        re_image = re.search(
            r'''(?:class="zoomPad"><img.*?src=")(?P<sImage>[^"]*?)(?:")''',
            html_content,
            re.S | re.I)
        if re_image is not None:
            image_name = re_image.group("sImage")
            comm.PLog.Log("image_name=%s" % image_name)


        return (prod_num, price, image_name, html_content)

    #**********************************************************************
    # 描  述： 价格信息入库
    #
    # 参  数： comp_id, 企业id
    # 参  数： fld_prod_id, 产品id
    # 参  数： fld_prod_price, 价格
    # 参  数： fld_prod_num, 销量
    #
    # 返回值： 空
    # 修  改：
    #**********************************************************************
    def load_to_db(self, comp_id, fld_prod_id, fld_prod_price, fld_prod_num):
        try:
            # 当前日期
            fld_now_date = time.strftime(
                '%Y-%m-%d', time.localtime(int(time.time())))

            # 查询是否已经存在
            sql = "select Id from wrk_360_products_price where prod_id='%s' and insert_time like '%s'" % (
                fld_prod_id, fld_now_date)
            (line_cnt, tbl_datas) = self.db_oper.exe_search(sql)
            if line_cnt > 0:
                # 更新操作
                sql = "update wrk_360_products_price set price=%s," \
                    "where prod_id='%s' and insert_time like '%s'" % (
                        fld_prod_price, fld_prod_id, fld_now_date)
                self.db_oper.exe_update(sql)
                comm.PLog.Log("更新操作！")
                return

            # 3
            # 插入操作
            #
            # 查询此产品最近的旧价格
            old_price = None
            sql = "select price from wrk_360_products_price where prod_id=%s order by id desc limit 1" % fld_prod_id
            (line_cnt, tbl_datas) = self.db_oper.exe_search(sql)
            if line_cnt > 0:
                old_price = tbl_datas[0]["price"]

            # 查询此产品最近的旧销量
            old_prod_num = None
            sql = "select prod_num from wrk_360_products_price where prod_id=%s order by id desc limit 1" % fld_prod_id
            (line_cnt, tbl_datas) = self.db_oper.exe_search(sql)
            if line_cnt > 0:
                old_prod_num = tbl_datas[0]["prod_num"]

            fld_inserttime = time.strftime("%Y-%m-%d %H:%M:%S")
            sql = "insert into wrk_360_products_price" \
                "(comp_id, prod_id, old_price, price, insert_time, old_prod_num, prod_num)" \
                "values(%s, %s, %s, %s, %s, %s, %s)"

            value = (comp_id,
                     fld_prod_id,
                     old_price,
                     fld_prod_price,
                     fld_inserttime,
                     old_prod_num,
                     fld_prod_num)
            self.db_oper.exe_insert(sql, value)
            comm.PLog.Log("入库完成")
        except:
            pass

    #**********************************************************************
    # 描  述： 请求服务器图片
    #
    # 参  数： thumb_img, 产品图片
    # 参  数： item, 数据字典
    #
    # 返回值：
    # 修  改：
    #**********************************************************************
    def request_thumb_image(self, product_id, thumb_img):

        # 判断是否已经存在于资源表
        sql = "select image_id from wrk_thumb_image_down where image_id = %s" % product_id
        (line_cnt, tbl_datas) = self.db_oper.exe_search(sql)
        if line_cnt > 0:
            # 放弃，不重复取
            comm.PLog.Log("先前已下载image!")
            return

        # 入库
        collect_time = time.strftime(
            '%Y-%m-%d %H:%M:%S', time.localtime(int(time.time())))
        sql = "insert into wrk_thumb_image_down(app_type, image_id, image_url, page_url, collect_time)" \
            " values (%s, %s, %s, %s, %s)"

        vals = ("360yaofang", product_id, thumb_img, "", collect_time)
        # 实时入库
        self.db_oper.exe_insert(sql, vals)

    #**********************************************************************
    # 描  述：任务完成报告
    #
    # 返回值：空
    # 修  改：
    #**********************************************************************
    def report_complate(self):
        comm.job_report.report_finish(
            self.job_id, self.job_stat, self.db_oper, self.web_name)


    #**********************************************************************
    # 描  述： 异常监控处理
    #　        若取到数据，且存在于异常保持表，则从异常保持表中移除
    #          若没有取到数据，且存在于异常保持表，则不处理。 且这种数据，在最终的定时任务中需要清除。
    #          若没有取到数据，且不存在于异常保持表，则需要周期性重试。 尽可能取到数据。
    #
    # 参  数： prod_id, 产品Id
    # 参  数： price, 价格信息
    # 参  数： url, 地址信息
    #
    # 返回值： 空
    # 修  改：
    #**********************************************************************
    def price_except_proc(self, comp_id, prod_id, price, url, html_content):
        if price is not None and price != 0:
            if prod_id in self.except_prods_set:
                # 从当前异表表删除
                comm.PLog.Log("去wrk_360_except_keep排除")
                sql = "delete from wrk_360_except_keep where prod_id=%s" % (
                    prod_id)
                self.db_oper.exe_search(sql)
        else:
            if prod_id in self.except_prods_set:
                comm.PLog.Log("异常保持!")
                # 不做任何处理, 避免已经下架的数据不断的重试。
                pass
            else:
                comm.PLog.Log("需要重试!")
                #获取异常原因码
                exp_cause_code = self.except_analyse(html_content)
                fld_now_date = time.strftime(
                    '%Y-%m-%d', time.localtime(int(time.time())))

                # 写重试表
                sql = "insert into wrk_360_except_now(comp_id, prod_id,exp_cause, exp_date) values(%s, %s, %s, %s)"
                vals = (comp_id , prod_id, exp_cause_code, fld_now_date)
                self.db_oper.exe_insert(sql, vals)
                
    #**********************************************************************
    # 描  述： 异常分析
    #
    # 参  数： html_content, 网页内容
    #
    # 返回值：
    # 修  改：
    #**********************************************************************
    def except_analyse(self, html_content):
        #异常枚举表, 见(bas_360_except_case)
        #0---正常
        #1---已下架
        #2---暂不销售
        #99---其它
        ret_case = 99;

        re_not_found = re.search(r'''(?:404\sNot\sFound</title>)''', html_content, re.S | re.I )
        if re_not_found != None:
            #1---已下架
            ret_case = 1

        if ret_case == 99:
            re_not_sase = re.search(r'''(?:暂不销售)''', html_content, re.S | re.I )
            if re_not_sase != None:
                #2----暂不销售
                ret_case = 2 

        return ret_case

