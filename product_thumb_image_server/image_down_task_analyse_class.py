#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 image_down_task_analyse_class.py
# VERSION: 	 1.0
# CREATED: 	 2016-05-31 13:08
# AUTHOR: 	 xuexiang
# DESCRIPTION:   图片下载任务分析程序
#
# HISTORY:
#*************************************************************
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import re
import os
import comm.PLog
import conf.db_conf
import comm.requests_pkg
from comm.db_helper import db_helper_class


class image_down_task_analyse_class():

    def __init__(self):
        # 分页大小
        self.page_size = 20
        self.m_db_oper = db_helper_class(conf.db_conf)

        pass

    def __del__(self):
        pass

    def do_main(self):
        # self.do_tao_qiang_gou_task()
        self.do_bao_jian_pin_task()
        pass

    #**********************************************************************
    # 描  述： 分析淘抢购任务
    #          此功能为一次性功能
    #
    # 返回值：
    # 修  改：
    #**********************************************************************
    def do_tao_qiang_gou_task(self):
        page_size = 100
        r_offset = 0

        # 获取任务总数
        sql = "select  sUrl, sInsertTime from wrk_taobao_qghd group by sUrl"
        (line_cnt, tbl_datas) = self.m_db_oper.exe_search(sql)
        comm.PLog.Log("任务总数: %d" % line_cnt)
        total_cnt = line_cnt

        proc_cnt = 0
        while True:
            sql = "select  sUrl, sInsertTime from wrk_taobao_qghd group by sUrl limit %d offset %d " % (
                page_size, r_offset)
            r_offset += page_size
            (line_cnt, tbl_datas) = self.m_db_oper.exe_search(sql)

            # 处理结束
            if line_cnt == 0:
                comm.PLog.Log("处理结束.")
                return

            for row_data in tbl_datas:
                try:
                    comm.PLog.Log(
                        "=============================================")
                    proc_cnt += 1
                    comm.PLog.Log("当前进度: %d/%d" % (proc_cnt, total_cnt))
                    fld_url = row_data["sUrl"]
                    fld_collect_time = row_data["sInsertTime"]

                    self.product_proc("", fld_url, fld_collect_time, "taoqianggou")

                except:
                    pass

    #**********************************************************************
    # 描  述： 处理保健品
    #
    # 返回值：
    # 修  改：
    #**********************************************************************
    def do_bao_jian_pin_task(self):
        page_size = 100
        r_offset = 0

        # 获取任务总数
        sql = "select product_url, collect_time from wrk_tmall_baojian_week group by product_url"
        (line_cnt, tbl_datas) = self.m_db_oper.exe_search(sql)
        comm.PLog.Log("任务总数: %d" % line_cnt)
        total_cnt = line_cnt

        proc_cnt = 0
        while True:
            sql = "select product_url, collect_time from wrk_tmall_baojian_week " \
                "group by product_url limit %d offset %d " % (
                    page_size, r_offset)
            r_offset += page_size
            (line_cnt, tbl_datas) = self.m_db_oper.exe_search(sql)

            # 处理结束
            if line_cnt == 0:
                comm.PLog.Log("处理结束.")
                return

            for row_data in tbl_datas:
                try:
                    comm.PLog.Log(
                        "=============================================")
                    proc_cnt += 1
                    comm.PLog.Log("当前进度: %d/%d" % (proc_cnt, total_cnt))
                    fld_url = row_data["product_url"]
                    fld_collect_time = row_data["collect_time"]

                    self.product_proc("", fld_url, fld_collect_time, "tmall_baojianpin")

                except:
                    pass

    def product_proc(self, product_id, product_url, collect_time, app_type):

        # 获取product_id: 为空时获取
        if not product_id:
            re_product_id = re.search(
                r'''(?:id=)(?P<sProductId>\d+)''', product_url, re.S | re.I )
            if re_product_id is None:
                comm.PLog.Log("丢弃URL: %s" % product_url)
                return

        product_id = re_product_id.group("sProductId")
        comm.PLog.Log("product_id: %s" % product_id)

        # 检查此Id是否已经存在于数据库中
        sql = "select image_id from wrk_thumb_image_down where app_type='%s' and image_id = '%s'" % (app_type, product_id)
        (line_cnt, tbl_datas) = self.m_db_oper.exe_search(sql)
        if line_cnt > 0:
            # 放弃，不重复取
            comm.PLog.Log("先前已下载!")
            return

        # 获取图片地址
        url = product_url
        if not product_url.startswith("http"):
            url = "https:" + product_url
        thumb_image_src = ""

        #url = "https://detail.tmall.com/item.htm?id=" + product_id
        (http_ok, resp) = comm.requests_pkg.get(url, max_try=3)
        if http_ok:
            resp_content = resp.content

            # 提取图片URL: 偿试天猫
            re_thumb_image = re.search(
                r'''(?:<div\s+class="tb-booth">.*?src=")(?P<sImageUrl>[^"]*?jpg)(?:")''',
                resp_content,
                re.S | re.I)
            if re_thumb_image is not None:
                thumb_image_src = re_thumb_image.group("sImageUrl")
                comm.PLog.Log("图片tmall地址: %s" % thumb_image_src)

            # 偿试淘宝
            re_thumb_image_tb = re.search(
                r'''(?:img\s+id="J_IMgBooth"\s+src=")(?P<sUrl>[^"]*?)(?:")''',
                resp_content,
                re.S | re.I)
            if re_thumb_image_tb is not None:
                thumb_image_src = re_thumb_image_tb.group("sUrl")
                comm.PLog.Log("图片taobao地址: %s" % thumb_image_src)

        # 入库
        sql = "insert into wrk_thumb_image_down(app_type, image_id, image_url, page_url, collect_time)" \
            " values (%s, %s, %s, %s, %s)"

        vals = (app_type, product_id, thumb_image_src, url, collect_time)
        # 实时入库
        self.m_db_oper.exe_insert(sql, vals)
