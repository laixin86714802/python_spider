#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 pm_jkw_main.py
# VERSION: 	 1.0
# CREATED: 	 2016-02-20 10:44
# AUTHOR: 	 xuexiang
# DESCRIPTION:   健客官网数据采集
#
# HISTORY:
#*************************************************************
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import conf.app_conf
import conf.class_conf
from pm_collect_class import pm_collect_class


if __name__ == '__main__':
    # 新建一个应用
    app = pm_collect_class()
    app.do_main(conf.class_conf.cls_zygw_jkw, "健客网")
