#!/usr/bin/python
#coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 tmall_health_prods_detail_main.py
# VERSION: 	 1.0
# CREATED: 	 2016-05-19 18:49
# AUTHOR: 	 xuexiang
# DESCRIPTION:   天猫保健品，下载详情页
#
# HISTORY: 
#*************************************************************
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
 
from tmall_health_prods_detail_class import tmall_health_prods_detail_class

if __name__ == '__main__':
    # 新建一个应用
    app = tmall_health_prods_detail_class()
    app.do_main()
     

