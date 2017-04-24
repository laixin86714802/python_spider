#!/usr/bin/python
#coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 pm_360haoyao_main.py
# VERSION: 	 1.0
# CREATED: 	 2016-06-13 11:51
# AUTHOR: 	 xuexiang
# DESCRIPTION:   360好药网数据采集
#
# HISTORY: 
#*************************************************************

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from pm_360_collect_class import pm_360_collect_class


if __name__ == '__main__':
    # 新建一个应用
    app = pm_360_collect_class()
    app.do_main()
