#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 requests_pkg.py
# VERSION: 	 1.0
# CREATED: 	 2016-01-14 20:25
# AUTHOR: 	 xuexiang
# DESCRIPTION:   requests类的包裹器
#
# HISTORY:
#*************************************************************
import time
import requests
from random_useragent import getRandomUA

#**********************************************************************
# 描  述： 获取静态网页
#
# 参  数： url，目标地址
# 参  数： max_try, 最大重试次数
# 参  数： timeout, 页面请求超时时间
#
# 返回值： 返回一个元组
# 修  改： 
#**********************************************************************
def get(url, cookies, proxies, max_try=5, timeout=10):
    try_count = 0
    try:
        h_heads = getRandomUA()
        resp = requests.get(url, headers=h_heads, proxies=proxies, timeout=timeout, cookies=cookies)
        try_count += 1
        if resp:
            return (True, resp)
    except:
        pass
