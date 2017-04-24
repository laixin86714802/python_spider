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
        if not content :
            return ""

        md5obj = hashlib.md5()
        md5obj.update(content)
        return md5obj.hexdigest().upper()

    #**********************************************************************
    # 描  述： 写承载页面日志
    #
    # 参  数： body, 响应
    # 参  数： strMd5, Md5值
    #
    # 返回值： 空
    # 修  改：
    #**********************************************************************
    @staticmethod
    def savePayloadLog(body, strMd5):
        # 2015012112200
        sFormatNow = time.strftime(
            '%Y%m%d%H%M%S', time.localtime(int(time.time())))
        logName = CommProcessor.runtime_log + "PayloadLog/P_" + \
            sFormatNow + "_" + strMd5 + ".html"
        fo = open(logName, "wb")
        print >> fo, body
        fo.flush()

    #**********************************************************************
    # 描  述： 写目标页面日志
    #
    # 参  数： body, 响应
    # 参  数： strmd5, Md5值
    #
    # 返回值： 空
    # 修  改：
    #**********************************************************************
    @staticmethod
    def saveTargetLog(body, strMd5):
        # 2015012112200
        sFormatNow = time.strftime(
            '%Y%m%d%H%M%S', time.localtime(int(time.time())))
        logName = CommProcessor.runtime_log + "TargetLog/T_" + \
            sFormatNow + "_" + strMd5 + ".html"
        fo = open(logName, "wb")
        print >> fo, body
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
        if not str_pattern:
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

