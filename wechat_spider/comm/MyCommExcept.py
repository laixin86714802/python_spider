#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 MyCommExcept.py
# VERSION: 	 1.0
# CREATED: 	 2016-02-08 19:50
# AUTHOR: 	 xuexiang
# DESCRIPTION:   自定义通用异常类
#
# HISTORY:
#*************************************************************


class MyCommExcept(Exception):

    def __init__(self, msg=''):
        self.msg = msg

    def __del__(self):
        pass
