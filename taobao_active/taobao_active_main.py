#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 taobao_active_main.py
# VERSION: 	 1.0
# CREATED: 	 2016-01-12 12:42
# AUTHOR: 	 xuexiang
# DESCRIPTION:   抓取淘宝活动数据
#
# HISTORY:
#*************************************************************
import requests
from taobao_active_class import taobao_active_class


if __name__ == '__main__':
    # 创建一个应用
    app = taobao_active_class()
    app.do_main()
