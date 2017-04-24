#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 tmall_health_prods_list_class.py
# VERSION: 	 1.0
# CREATED: 	 2016-05-17 09:26
# AUTHOR: 	 xuexiang
# DESCRIPTION:   天猫保键品采集
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
from comm.JobSta import JobSta
import comm.PLog
from comm.MyHttpDownFailed import MyHttpDownFailed
from comm.MyHttpParseFailed import MyHttpParseFailed


class tmall_health_prods_list_class():

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
        self.app_id = conf.app_conf.app_tmall_health_prods_list
        self.class_id = conf.class_conf.cls_tmall_health_prods_list
        self.job_id = "%s_%s_%s" % (time.strftime('T%Y%m%d%H%M'), self.app_id, self.class_id)
        


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
            max_page_no = 100
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
    def set_start(self):
        self.job_stat = JobSta()
        #999表示未知
        self.job_stat.all_task_count = 9999

        comm.PLog.Log("初始化job report.")
        comm.job_report.report_start(
            self.app_id,
            self.class_id,
            self.job_id,
            self.job_stat.all_task_count,
            self.m_db_obj)

    #**********************************************************************
    # 描  述： 总任务完成
    #
    # 返回值： 
    # 修  改： 
    #**********************************************************************
    def set_finish(self):
        comm.PLog.Log("set_finish")
        comm.job_report.report_finish( self.job_id, self.job_stat, self.m_db_obj, "")

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
            if req_page_no > 1 and req_page_no > self.m_page_count:
                return

            if req_page_no > 1:
                target_url = re.sub(
                    r'''pageNo=\d''',
                    "pageNo=" + str(req_page_no),
                    entry_url)

            # HTTP请求
            comm.PLog.Log("当前请求地址: %s" % target_url)
            self.m_browser.load(
                url=target_url,
                load_timeout=120,
                tries=3)

            # 注：very important!!!
            self.m_browser.wait(30)

            html_content = str(self.m_browser.html)

            # 只在首次请求时，分析页面数量
            if req_page_no == 1:
                self.m_shopid = shop_id

                # 分析链接
                str_pattern = r'''(?:<b\sclass="ui-page-s-len">\d/)(?P<sPageCount>\d+)(?:</b>)'''
                re_payload_page_count = re.search(
                    str_pattern, html_content, re.S | re.I)
                if re_payload_page_count is None:
                    comm.PLog.Log("re_payload_page_count=None!")
                    raise MyHttpParseFailed()

                self.m_page_count = int(
                    re_payload_page_count.group("sPageCount"))
                comm.PLog.Log("页面数量: %s" % self.m_page_count)

            # 页面解析
            self.parse_page(html_content)

            #统计
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
            raise MyHttpParseFailed()

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

                fld_url = "https://detail.tmall.com/item.htm?id=%s" % fld_product_id

                # 价格
                fld_price = ""
                re_price = re.search(
                    r'''<span\sclass="c-price">(.*?)</span>''', record, re.S)
                if re_price is not None:
                    fld_price = re_price.group(1).strip()

                # 标题
                fld_caption = ""
                re_caption = re.search(
                    r'''<img\salt="(.*?)"''', record, re.S | re.I )
                if re_caption is not None:
                    fld_caption = re_caption.group(1)

                #comm.PLog.Log("product_id: %s" % fld_product_id)
                #comm.PLog.Log("price: %s" % fld_price)
                #comm.PLog.Log("caption: %s" % fld_caption)

                item = {}
                item["fld_shop_id"] = self.job_id
                item["fld_product_id"] = fld_product_id
                item["fld_price"] = fld_price
                item["fld_caption"] = fld_caption
                item["fld_url"] = fld_url

                # 入库
                self.load_to_db(item)

                current_id = current_id + 1
            except:
                #raise
                pass

        comm.PLog.Log("获取商品数量：%d" % (current_id + 1))


    def load_to_db(self, item):
        sql = "insert into wrk_tmall_baojian_goods_list( sJobId, sSource, sProductId, sTargetUrl, sProductName, sPrice, sPageId, sCollectTime, sRemark ) values(%s, %s, %s, %s, %s, %s, %s, %s, %s)"

        fld_inserttime = time.strftime(
            '%Y-%m-%d %H:%M:%S', time.localtime(int(time.time())))

        vals = (
            self.job_id,
            self.m_shopid,
            item["fld_product_id"],
            item["fld_url"],
            item["fld_caption"],
            item["fld_price"],
            "",
            fld_inserttime,
            self.m_shop_name)
        self.m_db_obj.exe_insert(sql, vals)
