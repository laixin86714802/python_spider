#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 JobSta.py
# VERSION: 	 1.0
# CREATED: 	 2016-02-20 13:09
# AUTHOR: 	 xuexiang
# DESCRIPTION:   Job统计
#
# HISTORY:
#*************************************************************
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class JobSta():

    def __init__(self):
        # 任务总数量
        self.all_task_count = 0
        # 下载任务数
        self.down_ok_count = 0
        # 下载异常数量
        self.down_failed_count = 0
        # 解析异常数量
        self.parse_failed_count = 0
        # 解析异常数量
        self.other_failed_count = 0

    def __del__(self):
        pass

    def clear(self):
        self.all_task_count = 0
        self.down_ok_count = 0
        self.down_failed_count = 0
        self.parse_failed_count = 0
        self.other_failed_count = 0
