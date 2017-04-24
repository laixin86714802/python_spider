#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 kangaiduo_combo_main.py
# VERSION: 	 1.0
# CREATED: 	 2016-01-14 12:52
# AUTHOR: 	 xuexiang
# DESCRIPTION:   康爱多套装抓取
#
# HISTORY:
#*************************************************************
import sys
from kangaiduo_combo_class import kangaiduo_combo_class

if __name__ == '__main__':
    # 新建一个应用
    app = kangaiduo_combo_class()
    app.do_task()
