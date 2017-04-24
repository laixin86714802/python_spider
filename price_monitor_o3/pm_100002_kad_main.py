#!/usr/bin/python
#coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 pm_kad_main.py
# VERSION: 	 1.0
# CREATED: 	 2016-02-22 13:52
# AUTHOR: 	 xuexiang
# DESCRIPTION:   康爱多
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
    app.do_main(conf.class_conf.cls_zygw_kad, "康爱多")

