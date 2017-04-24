#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 taobao_active_class.py
# VERSION: 	 1.0
# CREATED: 	 2016-01-12 12:45
# AUTHOR: 	 xuexiang
# DESCRIPTION:   抓取淘宝活动数据
#
# HISTORY:       2016-02-23 wlt 采用基础类库重写,添加Job Report.
#
#*************************************************************
import re
import time
import comm.PLog
import comm.stone_funs
import comm.job_report
from comm.db_helper import db_helper_class
from comm.JobSta import JobSta
from comm.MyHttpDownFailed import MyHttpDownFailed
from comm.MyHttpParseFailed import MyHttpParseFailed
import conf.app_conf
import conf.class_conf
import conf.db_conf

from Item import Item
from WebkitBrowser import WebkitBrowser
from active_extractor import CommExtractor


class taobao_active_class():

    def __init__(self):
        self.db_oper = db_helper_class(conf.db_conf)

        # 应用：淘宝抢购
        self.app_id = conf.app_conf.app_tbhdqg_collect_id
        # 类别：淘宝抢购活动
        self.class_id = conf.class_conf.cls_tbhdqg
        # 名称
        self.web_name = "淘宝抢购"

        self.job_stat = JobSta()
        self.job_id = "%s_%s_%s" % (time.strftime(
            'T%Y%m%d%H%M'), self.app_id, self.class_id)

    def __del__(self):
        pass

    def do_main(self):
        # 总任务量：只有一个页面
        self.job_stat.all_task_count = 2
        comm.job_report.report_start(
            self.app_id,
            self.class_id,
            self.job_id,
            self.job_stat.all_task_count,
            self.db_oper)

        # 抓取医疗保健
        category = "医疗保健"
        comm.PLog.Log("下载分类：%s" % category)
        url = "https://qiang.taobao.com/category.htm?spm=a21bz.7725273.2164140.14.cp93bP&categoryId=317000"
        total_num_1 = self.do_task(category, url)

        # 抓取美妆
        category = "美妆"
        comm.PLog.Log("下载分类：%s" % category)
        url = "https://qiang.taobao.com/category.htm?spm=a21bz.7725273.2164140.5.7eY8st&categoryId=308000"
        total_num_2 = self.do_task(category, url)

        # 入库
        sRemark = "总共采集到%d=%d+%d个商品" % (total_num_1 +
                                        total_num_2, total_num_1, total_num_2)
        comm.job_report.report_finish(
            self.job_id, self.job_stat, self.db_oper, sRemark)

    #**********************************************************************
    # 描  述： 单页抓取
    #
    # 参  数： category, 活动分类
    # 参  数： target_url, 目标链接
    #
    # 返回值： 空
    # 修  改：
    #**********************************************************************
    def do_task(self, category, target_url):

        # 总共商品数量
        total_num = 0

        try:
            browser = WebkitBrowser()
            resp_content = browser.open(target_url)
            if resp_content is None:
                raise MyHttpDownFailed()

            # 去噪处理
            re_pure_data = re.search(
                CommExtractor.payload_puredata,
                resp_content, re.S | re.I)

            if re_pure_data is None:
                comm.PLog.Log("[WARNING] 去噪失败!")
                raise MyHttpParseFailed()

            comm.PLog.Log("去噪成功.")

            # 预计总计录数
            re_itemcnt = re.search(
                CommExtractor.payload_productcnt,
                re_pure_data.group(),
                re.S | re.I)
            if re_itemcnt is None:
                raise MyHttpParseFailed()
            comm.PLog.Log("预计条目数: %s" % (re_itemcnt.group("sProductCount")))
            
            # 分析抢购进行中的数据
            num1 = self.proc_qg_doing(category, re_pure_data.group())
            comm.PLog.Log("抢购进行中抓取数量:%d" % (num1))

            # 分析已经抢购完成的数据
            num2 = self.proc_qg_complted(category, re_pure_data.group())
            comm.PLog.Log("抢购已完成抓取数量:%d" % (num2))

            num3 = self.proc_qg_notbegin(category, re_pure_data.group())
            comm.PLog.Log("抢购未开始抓取数量:%d" % (num3))

            num4 = num1 + num2 + num3
            total_num = num4
            comm.PLog.Log("总抓取数量:%d" % (num4))

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
            raise
        finally:
            pass

        return total_num

    #**********************************************************************
    # 描  述： 处理已经完成的抢购
    #
    # 参  数： payload_puredata, 提纯数据
    #
    # 返回值： 空
    # 修  改：
    #**********************************************************************
    def proc_qg_complted(self, category, payload_puredata):
        # 实际抓取数量
        capture_count = 0

        re_record_blockIt = re.finditer(
            CommExtractor.payload_record_block_left0,
            payload_puredata,
            re.S | re.I)
        if re_record_blockIt is None:
            comm.PLog.Log("[WARNING] payload_record_block_left0匹配失败!")
        else:
            for record in re_record_blockIt:
                rem = re.search(
                    CommExtractor.payload_record_info_left0,
                    record.group(),
                    re.S | re.I)
                if rem is None:
                    comm.PLog.Log("rem eq None")
                else:
                    # 新建一个记录对象
                    item = Item()
                    item.category = category
                    item.title = rem.group("sTitle")
                    item.subtitle = rem.group("sSubTitle")
                    item.price = rem.group("sPrice")
                    item.rate = "100%"
                    item.num = rem.group("sNum")
                    item.url = ""

                    capture_count += 1
                    self.load_to_db(item, True)

        return capture_count

    #**********************************************************************
    # 描  述： 处理还在进行中的抢购
    #
    # 参  数： payload_puredata, 提纯数据
    #
    # 返回值： 空
    # 修  改：
    #**********************************************************************
    def proc_qg_doing(self, category, payload_puredata):
        # 实际抓取数量
        capture_count = 0

        re_record_blockIt = re.finditer(
            CommExtractor.payload_record_block_left99,
            payload_puredata,
            re.S | re.I)
        if re_record_blockIt is None:
            comm.PLog.Log("[WARNING] payload_record_block_left99匹配失败!")
        else:
            for record in re_record_blockIt:
                rem = re.search(
                    CommExtractor.payload_record_info_left99,
                    record.group(),
                    re.S | re.I)
                if rem is None:
                    comm.PLog.Log("rem == None")
                else:
                    # 新建一个记录对象
                    item = Item()
                    item.category = category
                    item.title = rem.group("sTitle")
                    item.subtitle = rem.group("sSubTitle")
                    item.price = rem.group("sPrice")
                    item.rate = rem.group("sRete")
                    item.num = rem.group("sNum")
                    item.url = rem.group("sUrl")
                    thumb_img = rem.group("sThumbImg")

                    # 获取product_id
                    re_product_id = re.search(
                        r'''(?:id=)(?P<sProductId>\d+)''', item.url, re.S | re.I )
                    if re_product_id is None:
                        comm.PLog.Log("丢弃URL: %s" % item.url)
                        continue

                    item.product_id = re_product_id.group("sProductId")

                    # 向资源注册
                    self.request_thumb_image(thumb_img, item)

                    capture_count += 1
                    self.load_to_db(item, False)

        return capture_count

    #**********************************************************************
    # 描  述： 没有开抢的产品
    #
    # 参  数： payload_puredata, 提纯数据
    #
    # 返回值： 空
    # 修  改：
    #**********************************************************************
    def proc_qg_notbegin(self, category, payload_puredata):
        # 实际抓取数量
        capture_count = 0

        re_record_blockIt = re.finditer(
            CommExtractor.payload_record_block_notbegin,
            payload_puredata,
            re.S | re.I)
        if re_record_blockIt is None:
            comm.PLog.Log("[WARNING] payload_record_block_notbegin匹配失败!")
        else:
            for record in re_record_blockIt:
                rem = re.search(
                    CommExtractor.payload_record_info_notbegin,
                    record.group(),
                    re.S | re.I)
                if rem is None:
                    comm.PLog.Log("rem == None")
                else:
                    # 新建一个记录对象
                    item = Item()
                    item.category = category
                    item.title = rem.group("sTitle")
                    item.subtitle = rem.group("sSubTitle")
                    item.price = rem.group("sPrice")
                    item.rate = "0%"
                    item.num = "0"
                    item.url = rem.group("sUrl")
                    thumb_img = rem.group("sThumbImg")

                    # 获取product_id
                    re_product_id = re.search(
                        r'''(?:id=)(?P<sProductId>\d+)''', item.url, re.S | re.I )
                    if re_product_id is None:
                        comm.PLog.Log("丢弃URL: %s" % item.url)
                        continue


                    item.product_id = re_product_id.group("sProductId")

                    # 向资源注册
                    self.request_thumb_image(thumb_img, item)

                    capture_count += 1
                    self.load_to_db(item, False)

        return capture_count

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
        product_id = item.product_id

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

        vals = ("taoqianggou", product_id, thumb_img, "", collect_time)
        # 实时入库
        self.db_oper.exe_insert(sql, vals)

    def load_to_db(self, item, is_complate):
        # 当前日期
        fld_now_date = time.strftime(
            '%Y-%m-%d', time.localtime(int(time.time())))

        # 当前时间
        fld_inserttime = time.strftime(
            '%Y-%m-%d %H:%M:%S', time.localtime(int(time.time())))

        # 查询是否已经存在
        if not is_complate:
            sql = "select Id from wrk_taobao_qghd where product_id='%s' and sInsertTime like '%s%%'" % (
                item.product_id, fld_now_date)
            (line_cnt, tbl_datas) = self.db_oper.exe_search(sql)
            if line_cnt > 0:
                # 更新操作
                sql = "update wrk_taobao_qghd set sRate='%s', nNum=%s " \
                    "where product_id='%s' and sInsertTime like '%s%%'" % (
                        item.rate, item.num, item.product_id, fld_now_date)
                self.db_oper.exe_update(sql)
                comm.PLog.Log("更新操作")
                return
        else:
            # 已经抢购完成
            sql = "select Id from wrk_taobao_qghd where sTitle='%s' and sSubTitle='%s' and sInsertTime like '%s%%'" % (
                item.title, item.subtitle, fld_now_date)
            (line_cnt, tbl_datas) = self.db_oper.exe_search(sql)
            if line_cnt > 0:
                # 更新操作
                sql = "update wrk_taobao_qghd set sRate='%s', nNum=%s " \
                    " where sTitle='%s' and sSubTitle='%s' and sInsertTime like '%s%%'" % (
                        item.rate, item.num, item.title, item.subtitle, fld_now_date)
                self.db_oper.exe_update(sql)
                comm.PLog.Log("更新操作")
                return

        # 插入操作
        sql = "insert into wrk_taobao_qghd(sJobId, sCategory, product_id, sTitle, \
                sSubTitle, fPrice, sRate, nNum, sUrl, sInsertTime) \
                values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

        vals = (
            self.job_id,
            item.category,
            item.product_id,
            item.title,
            item.subtitle,
            item.price,
            item.rate,
            item.num,
            item.url,
            fld_inserttime
        )

        # 实时入库
        self.db_oper.exe_insert(sql, vals)
