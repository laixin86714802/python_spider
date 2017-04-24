#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 downloadwebkit.py
# VERSION: 	 1.0
# CREATED: 	 2016-01-05 11:24
# AUTHOR: 	 xuexiang
# DESCRIPTION:
#
# HISTORY:
#*************************************************************
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import spynner
#import pyquery
import time
import sys
#import chardet


class WebkitBrowser():

    def __init__(self):
        # 创建一个浏览器对象
        self.browser = spynner.Browser()

        # 打开浏览器，并隐藏。
        self.browser.hide()
        #self.browser.show()

    def open(self, url0):
        html_body = ""
        try:
            h_heads = {
                "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"}
            # 加载页面, 超时时长120s
            #self.browser.load(url=url0, load_timeout=120, headers=h_heads)
            self.browser.load(url=url0, load_timeout=120)

            #将页面滚动条拖到底部
            js="var q=document.documentElement.scrollTop=10000"
            self.browser.runjs(js)
            self.browser.wait(15)
            #self.browser.wait_load(15)

            html_body = str(self.browser.html)
        except:
            # 下载动态网页失败
            html_body = ""

        return html_body
