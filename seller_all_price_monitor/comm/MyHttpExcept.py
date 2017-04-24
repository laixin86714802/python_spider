#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 MyHttpExcept.py
# VERSION: 	 1.0
# CREATED: 	 2016-02-08 19:50
# AUTHOR: 	 xuexiang
# DESCRIPTION:   自定义HTTP请求异常
#                碰到此类请求，一般需要重试
#
# HISTORY:
#*************************************************************
from HttpReq import HttpReq


class MyHttpExcept(Exception):

    #**********************************************************************
    # 描  述： 构造函数
    #
    # 参  数： http_req, HTTP请求
    # 参  数： dict_params, 其它参数列表
    #
    # 返回值： 空
    # 修  改：
    #**********************************************************************
    def __init__(self, http_req, dict_params={}):
        self.http_req = http_req
        self.params = dict_params

    def __del__(self):
        pass

    def get_cnt(self):
        return self.http_req.req_cnt
