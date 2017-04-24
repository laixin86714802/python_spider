#!/usr/bin/python
#coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME:      tmall_all_products_detail_class.py
# VERSION:   1.0
# CREATED:   2016-07-21 15:58
# AUTHOR:    xuexiang
# DESCRIPTION:   天猫店铺全量产品详情页采集
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
import traceback

import comm.PLog
import conf.app_conf
import conf.class_conf
import conf.db_conf
from comm.db_helper import db_helper_class
import comm.job_report
from comm.JobSta import JobSta
import comm.random_useragent

from comm.MyHttpDownFailed import MyHttpDownFailed
# from comm.MyHttpParseFailed import MyHttpParseFailed
# 通用处理器
# from comm.comm_processor import CommProcessor


class tmall_all_products_detail_class():

    def __init__(self):
        # 浏览器对象
        agent = comm.random_useragent.getRandomUAItem()
        # self.m_browser = spynner.Browser()
        self.m_browser = spynner.Browser(user_agent=agent)
        # self.m_browser.set_proxy("58.52.201.119:8080")
        self.m_browser.hide()
        # self.m_browser.show()

        # 创建数据库对象
        self.db_oper = db_helper_class(conf.db_conf)
        # 分页大小
        self.page_size = 20
        # 读取偏移值
        self.r_offset = 0

        # 当前进度
        self.curr_prog = 0
        # 总共丢弃记录数
        self.drop_count = 0

        # 应用：康爱多天猫全量商品详情
        #TODO: 
        # self.app_id = conf.app_conf.app_tmall_all_products_detail
        # self.class_id = conf.class_conf.cls_tmall_all_products_detail
        self.app_id = 999
        self.class_id = 999


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

        #TODO: wltsoft
        #
        # sql = "select sJobId from man_job_report_stat where nClassId=%s \
        # and sState='complate' order by id desc limit 1" % conf.class_conf.cls_tmall_all_products_list;
        # sql = "select sJobId from man_job_report_stat where nClassId=%s" \
        #     " and sState='complate' order by id desc limit 1" % 999;

        # (line_cnt, tbl_datas) = self.db_oper.exe_search(sql)
        # if line_cnt == 0:
        #     comm.PLog.Log("没有找到%s的任务Id")
        #     return
        # else:
            # last_list_jobid = tbl_datas[0]["sJobId"]
        last_list_jobid = "Q"
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
        task_id = "68907729"
        state = "1"
        sql = "select count(*) from tmall_list where sSource=%s and sState=%s" % (task_id, state)
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
            sql = "select sSource, sTargetUrl, sProductId"  \
                " from tmall_list where sSource=%s and sState=%s limit %d offset %d" % (
                task_id, state, self.page_size, self.r_offset)
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
                    product_id = row_data["sProductId"]

                    comm.PLog.Log("--------------------------------------")
                    comm.PLog.Log("下载目标: %s" % sTargetUrl)

                    #判断是否已经下载
                    sql = "select product_id" \
                        " from tmall_detail where product_id='%s'" % (product_id)
                    rcd_cnt = self.db_oper.get_count(sql)
                    if rcd_cnt > 0:
                        comm.PLog.Log("已经存在，不再取!")
                        continue

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
                    item['fld_url'] = sTargetUrl
                    item['fld_product_id'] = product_id
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

            # 促销价 || 价格
            item['fld_price_1'] = None
            item['fld_price_2'] = None
            # 促销价
            re_price = re.search(
                r'''(?:促销价</dt>\s*.*?tm-price">)(?P<sPrice>[^<]*?)(?:</span>)''',
                response_body,
                re.S | re.I)
            # 价格区间
            if re_price:
                re_prm_price = re_price.group("sPrice")
                prm_price = re.findall('''\d+\.\d+''', re_prm_price)
                if len(prm_price) == 1:
                    item['fld_price_1'] = prm_price[0]
                elif len(prm_price) == 2:
                    item['fld_price_1'] = prm_price[0]
                    item['fld_price_2'] = prm_price[1]
            else:
                # 价格
                re_price_normal = re.search(
                    r'''(?:价格</dt>\s*.*?tm-price">)(?P<sPrice>[^<]*?)(?:</span>)''',
                    response_body,
                    re.S | re.I)
                get_price = re_price_normal.group("sPrice")
                prm_price = re.findall('''\d+\.\d+''', get_price)
                if len(prm_price) == 1:
                    item['fld_price_1'] = prm_price[0]
                elif len(prm_price) == 2:
                    item['fld_price_1'] = prm_price[0]
                    item['fld_price_2'] = prm_price[1]

            # 产品名称
            re_prodname = re.search(
                r'''(?:class="tb-detail-hd">\s*<h1[^>]*?>\s*)(?P<sTitle>[^<]*?)(?:\s*</h1>)''',
                response_body, re.S | re.I)
            if re_prodname:
                item["fld_product_name"] = "".join((re_prodname.group("sTitle")).split())
            else:
                item["fld_product_name"] = ""

            # 月销量
            re_month_sale_cnt = re.search(
                r'''(?:>月销量</span><span\s*class="tm-count">)(?P<sMonthSaleCnt>\d+)''',
                response_body,
                re.S | re.I)
            if re_month_sale_cnt:
                item["fld_month_sale_cnt"] = "".join(
                re_month_sale_cnt.group("sMonthSaleCnt"))
            else:
                item["fld_month_sale_cnt"] = None

            # 批准文号|注册证号
            item["fld_approval_num"] = None
            item["fld_register_num"] = None
            re_approval_num = re.search(
                r'''(?:>批准文号:&nbsp;)(?P<sAppRovalNum>[^<]*)(?:</li>)''',
                response_body,
                re.S | re.I)
            if re_approval_num:
                approval_num = re_approval_num.group("sAppRovalNum")
                if "国药准字" in approval_num:
                    item["fld_approval_num"] = "".join(re_approval_num.group("sAppRovalNum"))
                else:
                    item["fld_register_num"] = "".join(re_approval_num.group("sAppRovalNum"))
            else:
                item["fld_approval_num"] = None
                item["fld_register_num"] = None

            # 注册证号
            if item["fld_register_num"] == None:
                re_register_num = re.search(
                    r'''(?:>注册证号:&nbsp;)(?P<sRegisterNum>[^<]*)(?:</li>)''',
                    response_body,
                    re.S | re.I)
                if re_register_num:
                    item["fld_register_num"] = re_register_num.group("sRegisterNum")
                else:
                    item["fld_register_num"] = None

            # 商品类型
            if re_month_sale_cnt != None and re_approval_num != None:
                item["fld_proudect_type"] = "OTC"
            elif re_month_sale_cnt != None and re_approval_num == None:
                item["fld_proudect_type"] = "其他"
            elif re_month_sale_cnt == None and re_approval_num != None:
                item["fld_proudect_type"] = "处方药"
            else:
                item["fld_proudect_type"] = None



            #comm.PLog.Log("=======================================================")
            product_id = item["fld_product_id"]
            comm.PLog.Log("ID: %s" % product_id)
            comm.PLog.Log("标题: %s" % (item["fld_product_name"]))
            # comm.PLog.Log("价格: %s" % (item["fld_price"]))
            comm.PLog.Log("销量: %s" % (item["fld_month_sale_cnt"]))

            #TODO:
            #re_thumb_image = re.search(
                #r'''(?:<div\s+class="tb-booth">.*?src=")(?P<sImageUrl>[^"]*?jpg)(?:")''',
                #response_body,
                #re.S | re.I)
            #if re_thumb_image is not None:
                #thumb_image_src = re_thumb_image.group("sImageUrl")
                #comm.PLog.Log("图片tmall地址: %s" % thumb_image_src)

            #thumb_img = re_thumb_image.group("sImageUrl")

            #self.request_thumb_image(thumb_img, item)

            # 入库
            self.load_to_db(item)
            self.job_stat.down_ok_count += 1

        # except MyHttpDownFailed as ex:
        #     comm.PLog.Log("下载异常!")
        #     self.job_stat.down_failed_count += 1
        # except MyHttpParseFailed() as ex:
        #     comm.PLog.Log("解析异常!")
        #     self.job_stat.parse_failed_count += 1
        except Exception,e:
            traceback.print_exc()
        # except:
        #     comm.PLog.Log("其它异常!")
        #     self.job_stat.other_failed_count += 1
        #     raise
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
            fld_inserttime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(time.time())))

            #查询此产品最近的销量
            # old_sale_num_30 = ""
            # sql = "select sale_num_30 from wrk_tmall_all_products_month" \
            #     " where product_id=%s order by id desc limit 1" % ( item["fld_product_id"])
            # (line_cnt, tbl_datas) = self.db_oper.exe_search(sql)
            # if line_cnt > 0:
            #     old_sale_num_30 = tbl_datas[0]["sale_num_30"]

            #查询此产品最近的旧价格
            # old_price = ""
            # sql = "select prm_price from wrk_tmall_all_products_month where product_id=%s" \
            #     " order by id desc limit 1" % ( item["fld_product_id"])
            # (line_cnt, tbl_datas) = self.db_oper.exe_search(sql)
            # if line_cnt > 0:
            #     old_price = tbl_datas[0]["prm_price"]

            sql = "insert into tmall_detail" \
                "(shop_id, product_id, product_name, sale_num_30," \
                " prm_price_min, prm_price_max, approval_num, register_num," \
                " product_url, collect_time, product_type)" \
                " values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

            vals = (
                item["sSource"],  # shop_id
                item["fld_product_id"],
                item["fld_product_name"],
                item["fld_month_sale_cnt"],
                item["fld_price_1"],
                item["fld_price_2"],
                item["fld_approval_num"],
                item["fld_register_num"],
                item["fld_url"],
                fld_inserttime,
                item["fld_proudect_type"]
            )

            # 实时入库
            self.db_oper.exe_insert(sql, vals)
            comm.PLog.Log("完成.")
        except IOError as e:
            print e
        except:
            info = sys.exc_info()
            print info[0], ":", info[1]
