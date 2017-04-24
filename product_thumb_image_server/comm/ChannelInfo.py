#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 ChannelInfo.py
# VERSION: 	 1.0
# CREATED: 	 2016-02-09 00:27
# AUTHOR: 	 xuexiang
# DESCRIPTION:   频道信息
#
# HISTORY:
#*************************************************************


class ChannelInfo:

    def __init__(self):
        # 频道名称
        self.name = ""
        # 频道URL
        self.url = ""

        # 商品总数量
        self.total_goods_cnt = 0
        # 当前商品已识别数量, [1, ?]
        self.curr_goods_cnt = 0
        #页面内商品顺序，[1,?]
        self.curr_inpage_order = 0

        # 页面总数量
        self.total_page_cnt = 0
        # 当前页面已识别量, [1, ?]
        self.curr_page_id= 0

    def __del__(self):
        pass

    def clear(self):
        self.total_goods_cnt = 0
        self.curr_goods_cnt = 0
        self.total_page_cnt = 0
        self.curr_page_cnt = 0
