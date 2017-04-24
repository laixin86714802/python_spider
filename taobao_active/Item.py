#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 Item.py
# VERSION: 	 1.0
# CREATED: 	 2016-01-12 14:16
# AUTHOR: 	 xuexiang
# DESCRIPTION:   输出Item对象
#
# HISTORY:
#*************************************************************


class Item:

    def __init__(self):
        # 分类
        self.category = ""
        # 产品Id
        self.product_id = ""
        # 标题
        self.title = ""
        # 副标题
        self.subtitle = ""
        # 促销价
        self.price = ""
        # 已抢百分比
        self.rate = ""
        # 已抢件数
        self.num = ""
        # 产品链接
        self.url = ""
