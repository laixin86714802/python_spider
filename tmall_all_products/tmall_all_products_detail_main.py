#!/usr/bin/python
#coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 tmall_all_products_detail_main.py
# VERSION: 	 1.0
# CREATED: 	 2016-07-21 15:59
# AUTHOR: 	 xuexiang
# DESCRIPTION:   天猫店铺全量产品采集
#
# HISTORY: 
#*************************************************************

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
 
from tmall_all_products_detail_class import tmall_all_products_detail_class

if __name__ == '__main__':
    # 新建一个应用
    app = tmall_all_products_detail_class()
    app.do_main()
     

