#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 data_proc_main.py
# VERSION: 	 1.0
# CREATED: 	 2016-02-25 13:03
# AUTHOR: 	 xuexiang
# DESCRIPTION:
#
# HISTORY:
#*************************************************************
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from data_proc_class import data_proc_class


if __name__ == '__main__':
    app = data_proc_class()
    app.do_main()
