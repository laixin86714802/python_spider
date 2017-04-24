#!/usr/bin/python
#coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 product_offline.py
# VERSION: 	 1.0
# CREATED: 	 2016-02-24 20:00
# AUTHOR: 	 xuexiang
# DESCRIPTION:   产品下架识别
#
# HISTORY:
#*************************************************************
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import re

def offline_jkw(resp_content):
    re_offline = re.search("请检查您输入的地址是否正确", resp_content, re.S | re.I )
    if re_offline == None:
        return False
    
    return True

def offline_kad(resp_content):
    pass
