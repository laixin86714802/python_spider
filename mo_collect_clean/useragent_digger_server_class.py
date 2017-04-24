#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 useragent_digger_server_class.py
# VERSION: 	 1.0
# CREATED: 	 2016-05-07 15:30
# AUTHOR: 	 xuexiang
# DESCRIPTION:   UserAgent信息挖掘
#
# HISTORY:
#*************************************************************
import os
import re
import comm.PLog
import subprocess
import urllib

class useragent_digger_server_class():

    def __init__(self):
        # PHP解析器
        self.m_php_digger = r"useragent_digger.php"
        pass

    def __del__(self):
        pass

    #**********************************************************************
    # 描  述： 获取终端信息 
    #
    # 参  数： 
    # 参  数： 
    #
    # 返回值： 
    # 修  改： 
    #**********************************************************************
    def get_terminal_info(self, ua_content):
        # 对参数进行编码
        param = {"ua": ua_content}
        fmt_ua_content = urllib.urlencode(param)

        #old算法
        command = "php -f %s %s" % (self.m_php_digger, fmt_ua_content)
        proc = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE)
        return_code = proc.wait()
        resp_result = proc.stdout.read()

        #phone##HUAWEI HonorChe2 4.0 ##Android:4.4.2##Chrome:30.0.0.0
        return resp_result

