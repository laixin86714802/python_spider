#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 HttpReq.py
# VERSION: 	 1.0
# CREATED: 	 2016-02-09 21:28
# AUTHOR: 	 xuexiang
# DESCRIPTION:   HTTP请求对象
#
# HISTORY:
#*************************************************************


class HttpReq:

    def __init__(self, url, req_cnt=1):
        # 请求地址
        self.url = url
        # 请求请数
        self.req_cnt = req_cnt

    def __del__(self):
        pass

    # 添加重试次数
    def add_retry(self):
        self.req_cnt += 1

    # 获取请求次数
    def get_cnt(self):
        return self.req_cnt
