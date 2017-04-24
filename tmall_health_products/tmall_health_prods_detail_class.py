#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 tmall_health_prods_detail_class.py
# VERSION: 	 1.0
# CREATED: 	 2016-05-19 17:52
# AUTHOR: 	 xuexiang
# DESCRIPTION:   天猫保健品详情页下载
#
# HISTORY:
#*************************************************************
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import re
import chardet
import time
import spynner

import comm.PLog
import conf.app_conf
import conf.class_conf
import conf.db_conf
from comm.db_helper import db_helper_class
import comm.job_report
from comm.JobSta import JobSta
import comm.random_useragent

from comm.MyHttpDownFailed import MyHttpDownFailed
from comm.MyHttpParseFailed import MyHttpParseFailed
# 通用处理器
from comm.comm_processor import CommProcessor


class tmall_health_prods_detail_class():

    def __init__(self):
        # 浏览器对象
        agent = comm.random_useragent.getRandomUAItem()
        # self.m_browser = spynner.Browser()
        self.m_browser = spynner.Browser(user_agent=agent)
        self.m_browser.hide()
        # self.m_browser.show()

        self.db_oper = db_helper_class(conf.db_conf)
        # 分页大小
        self.page_size = 20
        # 读取偏移值
        self.r_offset = 0

        # 当前进度
        self.curr_prog = 0
        # 总共丢弃记录数
        self.drop_count = 0

        # 应用：天猫保健品详情
        self.app_id = conf.app_conf.app_tmall_health_prods_detail
        self.class_id = conf.class_conf.cls_tmall_health_prods_detail

    def __del__(self):
        pass

    def do_main(self):
        self.r_offset = 0
        self.curr_prog = 0
        self.drop_count = 0

        # 创建任务Id
        self.job_stat = JobSta()
        self.job_id = "%s_%s_%s" % (time.strftime(
            'T%Y%m%d%H%M'), self.app_id, self.class_id)

        # 获取最近的列表JobId
        last_list_jobid = ""
        sql = "select sJobId from man_job_report_stat where nClassId=%s and sState='complate' order by id desc limit 1" % conf.class_conf.cls_tmall_health_prods_list;

        (line_cnt, tbl_datas) = self.db_oper.exe_search(sql)
        if line_cnt == 0:
            comm.PLog.Log("没有找到%s的任务Id")
            return
        else:
            last_list_jobid = tbl_datas[0]["sJobId"]
            comm.PLog.Log("最新任务是%s" % (last_list_jobid))
            self.do_task(last_list_jobid)

    #**********************************************************************
    # 描  述： 执行任务
    #
    # 参  数： task_id, 任务id
    #
    # 返回值： 空
    # 修  改：
    #**********************************************************************
    def do_task(self, task_id):

        sql = "select count(*) from wrk_tmall_baojian_goods_list where sJobId='%s'" % task_id
        # 任务总量
        self.job_stat.all_task_count = self.db_oper.get_count(sql)
        comm.PLog.Log("任务总量:%d" % self.job_stat.all_task_count)

        comm.PLog.Log("初始化job report.")
        comm.job_report.report_start(
            self.app_id,
            self.class_id,
            self.job_id,
            self.job_stat.all_task_count,
            self.db_oper)

        while True:
            # 从数据库分页读取数据
            sql = "select sSource, sTargetUrl, sProductId from wrk_tmall_baojian_goods_list where sJobId='%s' limit %d offset %d" % (
                task_id, self.page_size, self.r_offset)
            (line_cnt, tbl_datas) = self.db_oper.exe_search(sql)

            self.r_offset += self.page_size

            # 分页处理结束
            if line_cnt == 0:
                comm.PLog.Log("处理结束.")
                comm.job_report.report_finish(
                    self.job_id, self.job_stat, self.db_oper, "")

                return

            for row_data in tbl_datas:
                try:
                    sSource = row_data["sSource"]
                    sTargetUrl = row_data["sTargetUrl"]
                    sProductId = row_data["sProductId"]
                    sTargetUrl = row_data["sTargetUrl"]

                    comm.PLog.Log("--------------------------------------")
                    comm.PLog.Log("下载目标: %s" % sTargetUrl)
                    comm.PLog.Log(
                        "已经下载数:%d, 5次重试丢弃数%d" %
                        (self.curr_prog, self.drop_count))

                    time.sleep(2)

                    # HTTP请求
                    comm.PLog.Log("当前请求地址: %s" % sTargetUrl)
                    self.m_browser.load(
                        url=sTargetUrl,
                        load_timeout=120,
                        tries=3)
                    html_content = str(self.m_browser.html)
                    
                    item = {}
                    item["sSource"] = sSource
                    item["fld_product_id"] = sProductId
                    item["fld_url"] = sTargetUrl
                    self.parse_detail(sTargetUrl, html_content, item)
                except MyHttpDownFailed as ex:
                    comm.PLog.Log("下载异常!")
                    self.job_stat.down_failed_count += 1
                except:
                    pass

    def parse_detail(self, req_url, response_body, item):
        comm.PLog.Log("请求详情.")

        try:
            content_type = chardet.detect(response_body)
            if content_type['encoding'] != "UTF-8":
                response_body = response_body.decode(
                    content_type['encoding'], 'ignore')
                response_body = response_body.encode("utf-8", 'ignore')

            # 解析内容页
            self.curr_prog += 1

            # 促销价
            item["fld_price"] = ""
            re_price = re.search(
                r'''(?:class="tm-promo-price">.*?<span\s*class="tm-price">)(?P<sPrice>[\d\.]+)(?:</span>)''',
                response_body,
                re.S | re.I)
            if re_price:
                item["fld_price"] = "".join(re_price.group("sPrice"))

            # 产品名称
            item["fld_product_name"] = ""
            re_prodname = re.search(
                r'''(?:class="tb-detail-hd">\s*<h1[^>]*?>\s*)(?P<sTitle>[^<]*?)(?:\s*</h1>)''',
                response_body, re.S | re.I)
            if re_prodname:
                item["fld_product_name"] = "".join(
                    re_prodname.group("sTitle"))
                item["fld_product_name"] = CommProcessor.apaptRemoveSpace(
                    item["fld_product_name"])

            #comm.PLog.TempLog("m30.log", response_body)

            # 月销量
            re_month_sale_cnt = re.search(
                r'''(?:>月销量</span><span\s*class="tm-count">)(?P<sMonthSaleCnt>\d+)''',
                response_body,
                re.S | re.I)
            if re_month_sale_cnt:
                item["fld_month_sale_cnt"] = "".join(
                    re_month_sale_cnt.group("sMonthSaleCnt"))
            else:
                item["fld_month_sale_cnt"] = 0

            #comm.PLog.Log("=======================================================")
            product_id = item["fld_product_id"]
            comm.PLog.Log("ID: %s" % product_id)
            comm.PLog.Log("标题: %s" % (item["fld_product_name"]))
            comm.PLog.Log("价格: %s" % (item["fld_price"]))
            comm.PLog.Log("销量: %s" % (item["fld_month_sale_cnt"]))

            re_thumb_image = re.search(
                r'''(?:<div\s+class="tb-booth">.*?src=")(?P<sImageUrl>[^"]*?jpg)(?:")''',
                response_body,
                re.S | re.I)
            if re_thumb_image is not None:
                thumb_image_src = re_thumb_image.group("sImageUrl")
                comm.PLog.Log("图片tmall地址: %s" % thumb_image_src)

            thumb_img = re_thumb_image.group("sImageUrl")

            self.request_thumb_image(thumb_img, item)

            # 入库
            self.load_to_db(item)
            self.job_stat.down_ok_count += 1

        except MyHttpDownFailed as ex:
            comm.PLog.Log("下载异常!")
            self.job_stat.down_failed_count += 1
        except MyHttpParseFailed() as ex:
            comm.PLog.Log("解析异常!")
            self.job_stat.parse_failed_count += 1
        except:
            comm.PLog.Log("其它异常!")
            self.job_stat.other_failed_count += 1
            raise
        finally:
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
    def request_thumb_image(self, thumb_img, item):
        product_id = item["fld_product_id"]

        # 判断是否已经存在于资源表
        sql = "select image_id from wrk_thumb_image_down where image_id = %s" % product_id
        (line_cnt, tbl_datas) = self.db_oper.exe_search(sql)
        if line_cnt > 0:
            # 放弃，不重复取
            comm.PLog.Log("先前已下载!")
            return

        # 入库
        collect_time = time.strftime(
            '%Y-%m-%d %H:%M:%S', time.localtime(int(time.time())))
        sql = "insert into wrk_thumb_image_down(app_type, image_id, image_url, page_url, collect_time)" \
            " values (%s, %s, %s, %s, %s)"

        vals = ("tmall_baojianpin", product_id, thumb_img, "", collect_time)
        # 实时入库
        self.db_oper.exe_insert(sql, vals)


    def load_to_db(self, item):
        comm.PLog.Log("目标入库.")

        try:
            fld_inserttime = time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime(int(time.time())))

            #查询此产品最近的销量
            old_sale_num_30 = ""
            sql = "select sale_num_30 from wrk_tmall_baojian_week where product_id=%s order by id desc limit 1" % ( item["fld_product_id"])
            (line_cnt, tbl_datas) = self.db_oper.exe_search(sql)
            if line_cnt > 0:
                old_sale_num_30 = tbl_datas[0]["sale_num_30"]

            #查询此产品最近的旧价格
            old_price = ""
            sql = "select prm_price from wrk_tmall_baojian_week where product_id=%s order by id desc limit 1" % ( item["fld_product_id"])
            (line_cnt, tbl_datas) = self.db_oper.exe_search(sql)
            if line_cnt > 0:
                old_price = tbl_datas[0]["prm_price"]

            sql = "insert into wrk_tmall_baojian_week(shop_id, product_id, product_name, sale_num_30, old_sale_num_30, prm_price, old_price, product_url, image_name, collect_time) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

            vals = (
                item["sSource"],  # shop_id
                item["fld_product_id"],
                item["fld_product_name"],
                item["fld_month_sale_cnt"],
                old_sale_num_30,
                item["fld_price"],
                old_price,  # old_price
                item["fld_url"],
                "",  # image
                fld_inserttime
            )

            # 实时入库
            self.db_oper.exe_insert(sql, vals)
            comm.PLog.Log("完成.")
        except IOError as e:
            print e
        except:
            info = sys.exc_info()
            print info[0], ":", info[1]
