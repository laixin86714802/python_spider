#!/usr/bin/python
#coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 load_mysql_tool_main.py
# VERSION: 	 1.0
# CREATED: 	 2016-05-11 11:02
# AUTHOR: 	 xuexiang
# DESCRIPTION: 
#
# HISTORY: 
#*************************************************************
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from load_mysql_tool_calss import load_mysql_tool_calss

if __name__ == '__main__':
    app = load_mysql_tool_calss()
    app.do_main()
     
