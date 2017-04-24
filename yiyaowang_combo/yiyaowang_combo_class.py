#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 kangaiduo_combo_class.py
# VERSION: 	 1.0
# CREATED: 	 2016-01-14 17:07
# AUTHOR: 	 xuexiang
# DESCRIPTION:   康爱多疗程装和套装抓取类
#
# HISTORY:
#*************************************************************
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import traceback
import re
import time
from yyw_extractor import CommExtractor
import comm.PLog
import comm.stone_funs
import comm.job_report
import comm.requests_pkg
from Item import Item
from comm.db_helper import db_helper_class
from comm.JobSta import JobSta
from comm.MyHttpDownFailed import MyHttpDownFailed
from comm.MyHttpParseFailed import MyHttpParseFailed
import conf.app_conf
import conf.class_conf
import conf.db_conf


class yiyaowang_combo_class:

    def __init__(self):
        self.db_oper = db_helper_class(conf.db_conf)
        # 分页大小
        self.page_size = 20
        # 读取偏移值
        self.r_offset = 0

        self.kad_id = 100001

        # 应用：淘宝抢购
        self.app_id = conf.app_conf.app_yyw_taozhang
        # 类别：淘宝抢购活动
        self.class_id = conf.class_conf.cls_web_taozhuang_yyw

        self.job_stat = JobSta()
        self.job_id = "%s_%s_%s" % (time.strftime(
            'T%Y%m%d%H%M'), self.app_id, self.class_id)

        # 名称
        self.web_name = "壹药网疗程装套装"

        self.prog = 0

    def __del__(self):
        pass

    def do_task(self):
        # 总任务量
        sql = "select count(*) from bas_comweb_url where comp_id=%d " % self.kad_id
        self.job_stat.all_task_count = self.db_oper.get_count(sql)

        # 初始化Job Report
        comm.job_report.report_start(
            self.app_id,
            self.class_id,
            self.job_id,
            self.job_stat.all_task_count,
            self.db_oper, "kad套装")

        while True:
            # 从数据库分页读取数据
            sql = '''select jk_prod_id,  jk_prod_name, comp_id, comp_prod_id, url \
                    from bas_comweb_url where comp_id="%d" limit %d offset %d''' \
                    % (self.kad_id, self.page_size, self.r_offset)

            (line_cnt, tbl_datas) = self.db_oper.exe_search(sql)
            
            self.r_offset += self.page_size

            if line_cnt == 0:
                return

            for row_data in tbl_datas:
                comm.PLog.Log("==================================================")

                try:
                    item = Item()

                    item.jk_prod_id = row_data["jk_prod_id"]
                    item.jk_prod_name = row_data["jk_prod_name"]
                    item.comp_id = row_data["comp_id"]
                    item.comp_prod_id = row_data["comp_prod_id"]
                    item.url = row_data["url"]
                    comm.PLog.Log("jk_prod_id=%s, comp_prod_id=%s" % ( item.jk_prod_id, item.comp_prod_id))
                    comm.PLog.Log("url=%s" % item.url)

                    # 详情页用requests提取
                    (http_ok, resp) = comm.requests_pkg.get(item.url, max_try=3, timeout=15)
                    if not http_ok:
                        raise MyHttpDownFailed()
                    else:
                        self.parse_detail(item.url, resp.content, item)
                        self.job_stat.down_ok_count += 1
                except Exception,e:
                    print traceback.format_exc()
                # except MyHttpDownFailed as ex:
                #     comm.PLog.Log("下载异常!")
                #     self.job_stat.down_failed_count += 1
                # except MyHttpParseFailed as ex:
                #     comm.PLog.Log("解析异常!")
                #     self.job_stat.parse_failed_count += 1
                # except:
                #     comm.PLog.Log("其它异常!")
                #     self.job_stat.other_failed_count += 1
                # finally:
                #     pass

        # Job Report上报
        comm.job_report.report_finish(
            self.job_id, self.job_stat, self.db_oper, "壹药网套装")

    def parse_detail(self, req_url, content, item):
        comm.PLog.Log("进度:%d" % self.prog)
        self.prog += 1

        product_no = item.comp_prod_id
        comm.PLog.Log("请求sProductNo成功, sProductNo=%s" % (product_no))

        # 解析单品价格
        single_price = ""
        re_single = re.search(
            CommExtractor.detail_singleprice,
            content,
            re.S | re.I)
        if re_single:
            single_price = re_single.group("sSinglePrice")
            item.single_price = single_price

        # 解析item_id
        item_id = ""
        re_item_id = re.search(
            CommExtractor.detail_item_id,
            content,
            re.S | re.I)
        if re_item_id:
            item_id = re_item_id.group("sItemId")
            item.item_id = item_id
        # 解析materialtype
        materialtype = ""
        re_materialtype = re.search(
            CommExtractor.detail_materialtype,
            content,
            re.S | re.I)
        if re_materialtype:
            materialtype = re_materialtype.group("sMaterialtype")
            item.materialtype = materialtype

        # 解析疗程装
        self.parse_liaochenzhuang(content, product_no, item)

    #**********************************************************************
    # 描  述： 请求疗程装
    #
    # 参  数： product_no, 产品编号
    # 参  数： item, 数据项
    #
    # 返回值： 空
    # 修  改：
    #**********************************************************************
    def parse_liaochenzhuang(self, content, product_no, item):
        try:
            target_url = "http://www.111.com.cn/items/getComboInfo.action?id=%s&type=%s" % (item.item_id, item.materialtype)
            comm.PLog.Log("疗程装URL: " + target_url)
            (http_ok, resp) = comm.requests_pkg.get(target_url, max_try=5)
            if not http_ok:
                print "resp failed!"
            else:
                # 去噪
                resp_body = resp.content
                resp_body = resp_body.decode('GB2312', 'ignore')
                resp_body = resp_body.encode("utf-8", 'ignore')
                content = re.findall('''{"id".*?}]},''', resp_body, re.S | re.I)
                if content:
                    match_cnt = 0

                    for block_info in content:
                        # 套装价格
                        re_price = re.search('''(?:originalPrice":)(?P<price>\d+|\d+.\d+)(?:,")''', block_info, re.S | re.I)
                        # 套装名
                        re_prod_name = re.search('''(?:productName":")(?P<sProductName>.*?)(?:")''', block_info, re.S | re.I)
                        # 获取数量
                        # re_detail_count = re.search('''(?:detailCount":)(?P<sDetailCount>.*?)(?:,")''', block_info, re.S | re.I)
                        match_cnt += 1
                        item.combo_type = "疗程装"
                        if re_price:
                            item.combo_price = re_price.group("price")
                        # detail_count = 0
                        # if re_detail_count:
                        #     detail_count = re_price.group("sDetailCount")

                        if re_prod_name:
                            item.combo_name = re_prod_name.group("sProductName")
                            # item.combo_name = item.combo_name + ",数量:" +str(detail_count)
                            self.load_to_db(item)

                    if match_cnt == 0:
                        comm.PLog.Log("不存在疗程装!")
                    else:
                        comm.PLog.Log("存在疗程装数量:%d" % (match_cnt))

        except:
            print traceback.format_exc()

    #**********************************************************************
    # 描  述： 生成疗程装标签名称
    #
    # 参  数： use_day_num, 可使用天数，可以为0
    # 参  数： product_num, 产品数量
    # 参  数： price, 产品价格
    #
    # 返回值： 组合名称
    # 修  改：
    #**********************************************************************
    # def build_treatment_name(self, product_num, price):
    #     if use_day_num == "0":
    #         # http://www.360kad.com/product/898.shtml
    #         return "满%s盒每盒￥%s" % (product_num, price)
    #     else:
    #         # http://www.360kad.com/product/4271.shtml
    #         can_use_days = int(use_day_num) * int(product_num)
    #         return "满%s盒每盒￥%s,可使用%d天" % (product_num, price, can_use_days)

    def load_to_db(self, item):
        try:
            fld_inserttime = time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime(int(time.time())))
            # 入库
            sql = "insert into wrk_kad_package(sJobId, nJkProdId, sJkProdName, comp_id, comp_prod_id, fPrice, sComboType, sComboName, fComboPrice, dtInsertTime) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

            vals = (
                self.job_id,
                item.jk_prod_id,
                item.jk_prod_name,
                item.comp_id,
                item.comp_prod_id,
                item.single_price,
                item.combo_type,
                str(item.combo_name).strip(),
                item.combo_price,
                fld_inserttime
            )

            # 实时入库
            self.db_oper.exe_insert(sql, vals)
        except:
            print traceback.format_exc()
