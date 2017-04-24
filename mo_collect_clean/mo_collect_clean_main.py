#!/usr/bin/python
#coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 mo_collect_clean_main.py
# VERSION: 	 1.0
# CREATED: 	 2016-05-11 09:22
# AUTHOR: 	 xuexiang
# DESCRIPTION:   M端数据清洗
#                持久进程 
#
# HISTORY: 
#*************************************************************
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from mo_collect_clean_class import mo_collect_clean_class
 

if __name__ == '__main__':
    app = mo_collect_clean_class();
    app.do_task();
     
