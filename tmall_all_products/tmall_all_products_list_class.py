#!/usr/bin/python
#coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 tmall_all_products_list_class.py
# VERSION: 	 1.0
# CREATED: 	 2016-07-21 15:44
# AUTHOR: 	 xuexiang
# DESCRIPTION:   采集天猫店铺全量产品
#
# HISTORY: 
#*************************************************************


import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import spynner
import re
import time
import comm.random_useragent
import conf.db_conf
import comm.job_report
import conf.app_conf
import conf.class_conf
import comm.db_helper
import traceback
import comm.PLog


class tmall_all_products_list_class():

    #**********************************************************************
    # 描  述： 构造函数
    #
    # 返回值：
    # 修  改：
    #**********************************************************************
    def __init__(self):
        # 浏览器对象
        agent = comm.random_useragent.getRandomUAItem()
        # self.m_browser = spynner.Browser()
        self.m_browser = spynner.Browser(user_agent=agent)
        self.m_browser.hide()
        # self.m_browser.show()

        # 数据库对象
        self.m_db_obj = comm.db_helper.db_helper_class(conf.db_conf)

        # 清理会话
        self.clear_session()

        #作业标识
        #TODO:
        # self.app_id = conf.app_conf.app_tmall_all_products_list
        # self.class_id = conf.class_conf.cls_tmall_all_products_list
        self.app_id = 999
        self.class_id = 999
        self.job_id = "%s_%s_%s" % (time.strftime('T%Y%m%d%H%M'), self.app_id, self.class_id)
        self.job_id = "T201612311000_106_800010"



    #**********************************************************************
    # 描  述： 清理会话
    #
    # 返回值： 空
    # 修  改：
    #**********************************************************************
    def clear_session(self):
        self.m_page_count = -1
        self.m_shopid = ""
        self.m_shop_name = ""
        pass

    #**********************************************************************
    # 描  述： main主方法
    #
    # 参  数： entry_url, 入口URL
    # 参  数： shop_id, 店铺Id
    #
    # 返回值：
    # 修  改：
    #**********************************************************************
    def do_main(self, entry_url, shop_id, shop_name):

        try:
            # 处理新的店铺时，先清理会话
            self.clear_session()
            self.m_shop_name = shop_name
            min_page_no = 1
            max_page_no = 1000
            for page_no in range(min_page_no, max_page_no):
                self.do_list_page_req(entry_url, page_no, shop_id)
                pass
        except:
            pass

    #**********************************************************************
    # 描  述： 设置开始状态
    #
    # 返回值： 
    # 修  改： 
    #**********************************************************************
    # def set_start(self):
    #     self.job_stat = JobSta()
    #     #999表示未知
    #     self.job_stat.all_task_count = 9999

    #     comm.PLog.Log("初始化job report.")
    #     comm.job_report.report_start(
    #         self.app_id,
    #         self.class_id,
    #         self.job_id,
    #         self.job_stat.all_task_count,
    #         self.m_db_obj)

    #**********************************************************************
    # 描  述： 总任务完成
    #
    # 返回值： 
    # 修  改： 
    #**********************************************************************
    # def set_finish(self):
    #     comm.PLog.Log("set_finish")
    #     comm.job_report.report_finish( self.job_id, self.job_stat, self.m_db_obj, "")

    #**********************************************************************
    # 描  述： 请求列表页
    #
    # 参  数： entry_url, 入口URL
    # 参  数： req_page_no, 当前请求页面序号
    # 参  数：
    #
    # 返回值： 空
    # 修  改：
    #**********************************************************************
    def do_list_page_req(self, entry_url, req_page_no, shop_id):

        try:
            # 根据入口模板生成目标URL
            target_url = entry_url

            if req_page_no > 1:
                target_url = re.sub(
                    r'''pageNo=(\d+)''',
                    "pageNo=" + str(req_page_no),
                    entry_url)
            self.page_no = req_page_no

            # HTTP请求
            comm.PLog.Log("当前请求地址: %s" % target_url)
            self.m_browser.load(
                url=target_url,
                load_timeout=120,
                tries=3)

            # 注：very important!!!
            self.m_browser.wait(3)

            html_content = str(self.m_browser.html)

            # 只在首次请求时，分析页面数量
            if req_page_no != 0:
                self.m_shopid = shop_id

                # 分析链接
                str_pattern = r'''(?:<b\sclass="ui-page-s-len">\d+/)(?P<sPageCount>\d+)(?:</b>)'''
                re_payload_page_count = re.search(
                    str_pattern, html_content, re.S | re.I)
                if re_payload_page_count is None:
                    comm.PLog.Log("re_payload_page_count=None!")
                    return

                self.m_page_count = int(
                    re_payload_page_count.group("sPageCount"))
                comm.PLog.Log("页面数量: %s" % self.m_page_count)

            # 页面解析
            self.parse_page(html_content)

        except:
            print traceback.format_exc()
            self.job_stat.other_failed_count += 1
            
            info = sys.exc_info()
            print info[0], ":", info[1]
            #raise
        finally:
            pass

    #**********************************************************************
    # 描  述： 页面解析
    #
    # 参  数： html_content, 面面内容
    #
    # 返回值： 空
    # 修  改：
    #**********************************************************************
    def parse_page(self, html_content):

        # 获取负载
        payload_puredata = r'''(?:class="ui-page-s-next")(?P<sReserve>.*?)(?:<a\sclass="page-cur">)'''
        re_pure_data = re.search(payload_puredata, html_content, re.S | re.I)
        if re_pure_data is None:
            return

        pure_data = re_pure_data.group('sReserve')

        # 获取商品项
        payload_record_block = r'''<dl\s(.*?)</dl>'''
        reobj = re.compile(payload_record_block, re.S | re.I)
        lstRef = reobj.findall(pure_data)

        current_id = 0

        for record in lstRef:
            try:
                # 商品Id
                fld_product_id = ""
                re_product_id = re.search(
                    r'''data-id="(.*?)"''', record, re.S)
                if re_product_id is not None:
                    fld_product_id = re_product_id.group(1)

                fld_url = "https://detail.yao.95095.com/item.htm?id=%s" % fld_product_id
                # fld_url = "https://detail.tmall.com/item.htm?id=%s" % fld_product_id

                # 价格
                fld_price = ""
                re_price = re.search(
                    r'''<span\sclass="c-price">(.*?)</span>''', record, re.S)
                if re_price is not None:
                    fld_price = re_price.group(1)

                # 标题
                fld_caption = ""
                re_caption = re.search(
                    r'''<img\salt="(.*?)"''', record, re.S | re.I )
                if re_caption is not None:
                    fld_caption = re_caption.group(1)

                # 总销量是否存在
                fld_salebool = ""
                fld_state = ""
                re_salebool = re.search(
                    r'''<span\sclass="sale-num">(\d+)</span>''', record, re.S | re.I)
                if re_salebool is not None:
                    fld_salebool = re_salebool.group(1)
                    fld_state = "1"
                else:
                    fld_salebool = ""
                    fld_state = "0"

                # comm.PLog.Log("product_id: %s" % fld_product_id)
                # comm.PLog.Log("price: %s" % fld_price)
                # comm.PLog.Log("caption: %s" % fld_caption)

                item = {}
                item["fld_shop_id"] = self.job_id
                item["fld_product_id"] = fld_product_id
                item["fld_price"] = str(fld_price)
                item["fld_caption"] = fld_caption
                item["fld_url"] = fld_url
                item["fld_salebool"] = fld_salebool
                item["fld_state"] = fld_state

                # 入库
                self.load_to_db(item)

                current_id = current_id + 1
            except:
                #raise
                pass
        comm.PLog.Log("当前页数:%s" % (self.page_no))
        comm.PLog.Log("获取商品数量：%d" % (current_id))

        # 写入临时日志
        time_now = time.strftime('[%Y-%m-%d %H:%M:%S]',time.localtime(int(time.time())))
        log_string = str(time_now) + "当前页数:" + str(self.page_no) + "获取商品数量:" + str(current_id)
        f = open("./runlog.txt","ab")
        f.write(log_string + "\n")
        f.close()


    def load_to_db(self, item):
        sql = "insert into tmall_list(sJobId, sSource, sProductId, sProductName, sPrice, sTargetUrl, sale_num_all, sState, sPageId, sCollectTime, sRemark) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

        fld_inserttime = time.strftime(
            '%Y-%m-%d %H:%M:%S', time.localtime(int(time.time())))

        vals = (
            self.job_id,
            self.m_shopid,
            item["fld_product_id"],
            item["fld_caption"],
            item["fld_price"],
            item["fld_url"],
            item["fld_salebool"],
            item["fld_state"],
            self.page_no,
            fld_inserttime,
            self.m_shop_name)
        self.m_db_obj.exe_insert(sql, vals)

