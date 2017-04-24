#!/usr/bin/python
#coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 image_down_task_analyse_main.py
# VERSION: 	 1.0
# CREATED: 	 2016-05-31 13:17
# AUTHOR: 	 xuexiang
# DESCRIPTION: 
#
# HISTORY: 
#*************************************************************
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from image_down_task_analyse_class import image_down_task_analyse_class
 
if __name__ == '__main__':
    app = image_down_task_analyse_class()
    app.do_main()
     
