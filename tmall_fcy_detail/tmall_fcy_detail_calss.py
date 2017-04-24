#!/usr/bin/python
# -*- coding:utf-8 -*-
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME:      TmSpider.py
# VERSION:   1.0
# CREATED:   2016-01-04 15:22
# AUTHOR:    xuexiang
# DESCRIPTION:   天猫详页下载
#
# HISTORY:
#*************************************************************
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import re
import chardet
import time
import HTMLParser

import comm.PLog
import comm.requests_pkg
import conf.app_conf
import conf.class_conf
import conf.db_conf
from comm.db_helper import db_helper_class
import comm.job_report
from comm.JobSta import JobSta
from comm.MyHttpDownFailed import MyHttpDownFailed
from comm.MyHttpParseFailed import MyHttpParseFailed

# 通用处理器
from comm.comm_processor import CommProcessor
# 通用规则提取器
from ffy_extractor import CommExtractor


class tmall_fcy_detail_calss():

    def __init__(self):
        self.db_oper = db_helper_class(conf.db_conf)
        # 分页大小
        self.page_size = 20
        # 读取偏移值
        self.r_offset = 0

        # 当前进度
        self.curr_prog = 0
        # 总共丢弃记录数
        self.drop_count = 0

        # 应用：天猫处方药详情
        self.app_id = conf.app_conf.app_tmfcy_detail_id

    def __del__(self):
        pass

    def do_task_byshop(self, company):
        self.r_offset = 0
        self.curr_prog = 0
        self.drop_count = 0

        # 类别：康爱多天猫处方药详情
        if company == "kad":
            self.class_id = conf.class_conf.cls_tmfcy_detail_kad
            self.list_class_id = conf.class_conf.cls_tmfcy_kad
        else:
            self.class_id = conf.class_conf.cls_tmfcy_detail_jk
            self.list_class_id = conf.class_conf.cls_tmfcy_jk

        # 创建任务Id
        self.job_stat = JobSta()
        self.job_id = "%s_%s_%s" % (time.strftime(
            'T%Y%m%d%H%M'), self.app_id, self.class_id)

        # 获取最近的列表JobId
        sql = "select sJobId from man_job_report_stat where nClassId=%s and sState='complate' order by id desc limit 1" % self.list_class_id

        print sql
        (line_cnt, tbl_datas) = self.db_oper.exe_search(sql)
        if line_cnt == 0:
            comm.PLog.Log("没有找到%s的任务Id")
            return
        else:
            last_list_jobid = tbl_datas[0]["sJobId"]
            comm.PLog.Log("%s的最新任务是%s" % (company, last_list_jobid))
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

        sql = "select count(*) from wrk_tmall_fcy_goods_list where sJobId='%s'" % task_id
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
            sql = "select sTargetUrl, sSource, sCarryingInfo, sProductId, sRemark from wrk_tmall_fcy_goods_list where sJobId='%s' limit %d offset %d" % (task_id, self.page_size, self.r_offset)

            (line_cnt, tbl_datas) = self.db_oper.exe_search(sql)

            self.r_offset += self.page_size

            if line_cnt == 0:
                comm.PLog.Log("处理结束.")
                comm.job_report.report_finish(
                    self.job_id, self.job_stat, self.db_oper, "")

                return

            for row_data in tbl_datas:
                try:
                    sTargetUrl = row_data["sTargetUrl"]
                    sProductId = row_data["sProductId"]
                    sSource = row_data["sSource"]
                    sCarryInfo = row_data["sCarryingInfo"]
                    sRemark = row_data["sRemark"]

                    comm.PLog.Log("--------------------------------------")
                    comm.PLog.Log("下载目标: %s" % sTargetUrl)
                    comm.PLog.Log(
                        "已经下载数:%d, 5次重试丢弃数%d" %
                        (self.curr_prog, self.drop_count))

                    time.sleep(2)

                    # 详情页用requests提取
                    (http_ok, resp) = comm.requests_pkg.get(sTargetUrl, max_try=5)
                    if http_ok:
                        item = {}
                        item["fld_caption"] = sCarryInfo.encode('utf-8')
                        item["fld_company"] = sSource.encode('utf-8')
                        item["fld_url"] = sTargetUrl
                        item["fld_remark"] = sRemark
                        item["fld_productid"] = sProductId
                        self.parse_detail(sTargetUrl, resp.content, item)
                    else:
                        self.drop_count += 1
                        comm.PLog.Log("重试5次均失败, 放弃!")
                except MyHttpDownFailed as ex:
                    comm.PLog.Log("下载异常!")
                    self.job_stat.down_failed_count += 1
                except:
                    pass

    def parse_detail(self, req_url, response_body, item):
        comm.PLog.Log("请求详情.")

        try:
            # 判断是否需要登录
            # CommProcessor.is_need_login(response_body)

            # content_type = chardet.detect(response_body)
            # if content_type['encoding'] != "UTF-8":
            #     response_body = response_body.decode(
            #         content_type['encoding'], 'ignore')
            #     response_body = response_body.encode("utf-8", 'ignore')

            # 去噪
            re_pure_data = re.search(
                CommExtractor.target_puredata,
                response_body, re.S | re.I)

            if re_pure_data is None:
                return
                ## 重新请求
                #comm.PLog.Log("目标页去噪匹配不到，重新请求:" + req_url)
                #try:
                        ## 详情页用requests提取
                        #(http_ok, resp) = comm.requests_pkg.get(req_url, max_try=5)
                        #if http_ok:
                            #self.parse_detail(req_url, resp.content, item)
                            #return
                        #else:
                            #self.drop_count += 1
                            #comm.PLog.Log("重试5次均失败, 放弃!")
                            #return
                #except:
                    #pass
            # 获取去噪内容,其中sReserve为CommExtractor.target_puredata中定义
            re_res_body = re_pure_data.group("sReserve")
            # 解析内容页
            self.curr_prog += 1
            html_parser = HTMLParser.HTMLParser()

            # 产品Id
            # re_productid = re.search(
            #     r'''(?:&id=)(?P<sId>\d+)''', item["fld_url"], re.S | re.I )
            # if re_productid:
            #     item["fld_productid"] = "".join(
            #         re_productid.group("sId"))
            #     comm.PLog.Log("产品ID: %s" % item["fld_productid"])

            # 产品价格
            re_price = re.search(
                r'''(?:"defaultItemPrice":")(?P<sPrice>[\d\.]+)''',
                response_body,
                re.S | re.I)
            if re_price:
                item["fld_price"] = "".join(re_price.group("sPrice"))

            # 产品名称
            re_prodname = re.search(
                r'''(?:<li[^>]*?>产品名称：)(?P<sProductName>[^<]*?)(?:</li>)''',
                re_res_body, re.S | re.I)
            if re_prodname:
                item["fld_productname"] = "".join(
                    re_prodname.group("sProductName"))
                item["fld_productname"] = CommProcessor.apaptRemoveSpace(
                    item["fld_productname"])
            else:
                item["fld_productname"] = ""

            # 药品通用名
            re_goodsname = re.search(
                r'''(?:>药品名称:\s*)(?P<sGoodsname>[^<]*?)(?:</li>)''',
                re_res_body, re.S | re.I)
            if re_goodsname:
                item["fld_commname"] = "".join(
                    re_goodsname.group("sGoodsname"))
                item["fld_commname"] = html_parser.unescape(
                    CommProcessor.apaptRemoveSpace(item["fld_commname"]))
            else:
                item["fld_commname"] = ""

            # 批准文号
            re_approvalno = re.search(
                r'''(?:>批准文号:.*?)(?P<sApprovalno>[A-Z\d]{6,})(?:[^<>]*</li>)''',
                re_res_body, re.S | re.I)
            if re_approvalno:
                item["fld_approvalno"] = "".join(
                    re_approvalno.group("sApprovalno"))
                item["fld_approvalno"] = html_parser.unescape(
                    CommProcessor.apaptRemoveSpace(item["fld_approvalno"]))
            else:
                item["fld_approvalno"] = ""

            # 规格
            re_spec = re.search(
                r'''(?:>药品规格:\s*)(?P<sSpec>[^<]*?)(?:</li>)''',
                re_res_body, re.S | re.I)
            if re_spec:
                item["fld_Spec"] = "".join(re_spec.group("sSpec"))
                item["fld_Spec"] = html_parser.unescape(
                    CommProcessor.apaptRemoveSpace(item["fld_Spec"]))
            else:
                item["fld_Spec"] = ""

            # 当前时间
            item["fld_inserttime"] = time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime(int(time.time())))

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
        finally:
            pass

    def load_to_db(self, item):
        comm.PLog.Log("目标入库.")

        try:
            fld_inserttime = time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime(int(time.time())))
            sql = "insert into wrk_tmall_fcy_goods_detail(sJobId, sCompany, sProductId, sProductName, fPrice, sApprovalNo, sSpec, sUrl, sInserttime, sRemark) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

            vals = (
                self.job_id,
                item["fld_company"],
                item["fld_productid"],
                item["fld_caption"],
                item["fld_price"],
                item["fld_approvalno"],
                item["fld_Spec"],
                item["fld_url"],
                fld_inserttime,
                item["fld_remark"]
            )

            # 实时入库
            self.db_oper.exe_insert(sql, vals)
            comm.PLog.Log("完成.")
        except IOError as e:
            print e
        except:
            info = sys.exc_info()
            print info[0], ":", info[1]
