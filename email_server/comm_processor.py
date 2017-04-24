#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 comm_processor.py
# VERSION: 	 1.0
# CREATED: 	 2016-01-11 10:24
# AUTHOR: 	 xuexiang
# DESCRIPTION:   通用处理器
#
# HISTORY:
#*************************************************************
import hashlib
import time
import re


class CommProcessor:
    runtime_log = "./Runtime/"

    #**********************************************************************
    # 描  述： 计算输出内容的MD5, 32位
    #
    # 参  数： content, 输入内容串
    #
    # 返回值： 大写的32位MD5值
    # 修  改：
    #**********************************************************************
    @staticmethod
    def getmd5(content):
        if content is None:
            return ""

        md5obj = hashlib.md5()
        md5obj.update(content)
        return md5obj.hexdigest().upper()

    #**********************************************************************
    # 描  述： 告警接口
    #
    # 参  数： content, 告警内容
    #
    # 返回值： 空
    # 修  改：
    #**********************************************************************
    @staticmethod
    def alarmReport(content):
        pass

    #**********************************************************************
    # 描  述： 写承载页面日志
    #
    # 参  数： response, 响应
    # 参  数： strMd5, Md5值
    #
    # 返回值： 空
    # 修  改：
    #**********************************************************************
    @staticmethod
    def savePayloadLog(response, strMd5):
        # 2015012112200
        sFormatNow = time.strftime(
            '%Y%m%d%H%M%S', time.localtime(int(time.time())))
        logName = CommProcessor.runtime_log + "/PayloadLog/P_" + \
            sFormatNow + "_" + strMd5 + ".html"
        fo = open(logName, "wb")
        print >> fo, response.body
        fo.flush()

    #**********************************************************************
    # 描  述： 写目标页面日志
    #
    # 参  数： response, 响应
    # 参  数： strmd5, Md5值
    #
    # 返回值： 空
    # 修  改：
    #**********************************************************************
    @staticmethod
    def saveTargetLog(response, strMd5):
        # 2015012112200
        sFormatNow = time.strftime(
            '%Y%m%d%H%M%S', time.localtime(int(time.time())))
        logName = CommProcessor.runtime_log + "/TargetLog/T_" + \
            sFormatNow + "_" + strMd5 + ".html"
        fo = open(logName, "wb")
        #print >> fo, response.body
        print >> fo, response
        fo.flush()

    #**********************************************************************
    # 描  述： 写承载链接
    #
    # 参  数： url, 链接对象
    #
    # 返回值： 空
    # 修  改：
    #**********************************************************************
    @staticmethod
    def savePayloadUrls(url):
        f_payload = open(CommProcessor.runtime_log + "payload_urls.log", "ab")
        print >> f_payload, url

    #**********************************************************************
    # 描  述：写承载链接
    #
    # 参  数：url, 链接对象
    #
    # 返回值：空
    # 修  改：
    #**********************************************************************
    @staticmethod
    def saveTargetUrls(url):
        f_target = open(CommProcessor.runtime_log + "target_urls.log", "ab")
        print >> f_target, url

    #**********************************************************************
    # 描  述： 从正则表达式中获取捕获组名称列表
    #
    # 参  数： str_pattern, 正则式
    #
    # 返回值： 捕获组名称列表
    # 修  改：
    #**********************************************************************
    @staticmethod
    def getCaptureNameList(str_pattern):
        if str_pattern is None:
            return []

        return re.findall(
            r'''(?:\(\?P<)(?P<sCaptureName>\w+)(?:>)''', str_pattern, re.S | re.I)

    #**********************************************************************
    # 描  述： 适配器， 去除两边的空白
    #
    # 参  数： content, 需要适配的字段内容
    #
    # 返回值：
    # 修  改：
    #**********************************************************************
    @staticmethod
    def apaptRemoveSpace(content):
        ret = re.sub("(&nbsp;)+", "", content)
        return ret

    @staticmethod
    def Log(content):
        fo = open(CommProcessor.runtime_log + "/runtime.log", "ab")
        currtm = time.strftime('[%Y-%m-%d %H:%M:%S]',
                               time.localtime(int(time.time())))
        print >>fo, currtm, content
        fo.flush()

        print "%s %s" % (currtm, content.decode("utf-8", "ignore").encode("gbk", "ignore"))

    @staticmethod
    def output(item):
        file = open(CommProcessor.runtime_log + "/out.dat", "ab")

        # 企业名称
        file.write(item["fld_company"].strip())
        file.write("##")
        # 承载MD5
        file.write(item["fld_payloadmd5"].strip())
        file.write("##")
        # 目标MD5
        file.write(item["fld_targetmd5"].strip())
        file.write("##")
        # 产品Id
        file.write(item["fld_productid"].strip())
        file.write("##")
        # 产品名称
        file.write(item["fld_productname"].strip())
        file.write("##")
        # 药品通用名
        file.write(item["fld_commname"].strip())
        file.write("##")
        # 产品标题
        file.write(item["fld_caption"].strip())
        file.write("##")
        # 促销价
        file.write(item["fld_price"])
        file.write("##")
        # 批准文号
        file.write(item["fld_approvalno"])
        file.write("##")
        # 规格
        file.write(item["fld_Spec"])
        file.write("##")
        # 目标URL
        file.write(item["fld_url"])
        file.write("##")
        # 当前时间
        file.write(item["fld_inserttime"])
        file.write("##")
        # 备注
        file.write(item["fld_remark"])
        file.write("\r\n")
        file.flush()

    #**********************************************************************
    # 描  述：当断当前是否需要登录天猫
    #
    # 参  数：html_body, 响应消息体
    #
    # 返回值：
    # 修  改：
    #**********************************************************************
    @staticmethod
    def is_need_login(html_body):
        str_need_login = r'''(?P<sLogin><title>上天猫，就够了</title>)'''
        re_needlogin = re.search(str_need_login, html_body, re.S | re.I)
        if re_needlogin:
            print "[WARING] 需要登录天猫!".decode("utf-8", 'ignore').encode("gbk", "ignore")
            # 需要登录
            return True

        # 不需要登录
        return False
