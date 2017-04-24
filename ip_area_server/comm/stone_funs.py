#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 stone_funs.py
# VERSION: 	 1.0
# CREATED: 	 2016-02-10 04:23
# AUTHOR: 	 xuexiang
# DESCRIPTION:   通用处理函数
#
# HISTORY:
#*************************************************************
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import chardet


#**********************************************************************
# 描  述： 将下的网页文件转换为UTF8
#
# 参  数： response_body, 网页源码
#
# 返回值： 转码后的UTF8数据
# 修  改：
#**********************************************************************
def ToUtf8(response_body):
    content_type = chardet.detect(response_body)
    #返回值
    #{'confidence': 0.0, 'encoding': None}
    #{'confidence': 0.99, 'encoding': 'GB2312'}

    if content_type != None:
        curr_code = content_type["encoding"].upper()
        if curr_code != "UTF-8":
            response_body = response_body.decode(curr_code, 'ignore')
            response_body = response_body.encode("utf-8", 'ignore')

    return response_body
