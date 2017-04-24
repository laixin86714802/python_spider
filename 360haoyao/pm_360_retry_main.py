#!/usr/bin/python
#coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 pm_360_retry_main.py
# VERSION: 	 1.0
# CREATED: 	 2016-06-13 16:50
# AUTHOR: 	 xuexiang
# DESCRIPTION:   异常重采
#
# HISTORY:
#*************************************************************

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from pm_360_retry_main import pm_360_retry_main


if __name__ == '__main__':
    app = pm_360_retry_main()
    app.do_main()
