#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 MyHttpDownFailed.py
# VERSION: 	 1.0
# CREATED: 	 2016-02-08 19:50
# AUTHOR: 	 xuexiang
# DESCRIPTION:   HTTP下载失败异常
#
# HISTORY:
#*************************************************************


class MyHttpDownFailed(Exception):

    def __init__(self, msg=''):
        self.msg = msg

    def __del__(self):
        pass
