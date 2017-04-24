#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 tmall_fcy_detail_main.py
# VERSION: 	 1.0
# CREATED: 	 2016-01-23 15:10
# AUTHOR: 	 xuexiang
# DESCRIPTION:   天猫处方药全量抓取
#
# HISTORY:
#*************************************************************
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from tmall_fcy_detail_calss import tmall_fcy_detail_calss

if __name__ == '__main__':
    # 新建一个应用
    app = tmall_fcy_detail_calss()
    app.do_task_byshop("kad")
