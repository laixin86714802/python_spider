#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 pm_retry_main.py
# VERSION: 	 1.0
# CREATED: 	 2016-03-09 16:27
# AUTHOR: 	 xuexiang
# DESCRIPTION:
#
# HISTORY:
#*************************************************************
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from pm_retry_class import pm_retry_class


if __name__ == '__main__':
    app = pm_retry_class()
    app.do_main()
