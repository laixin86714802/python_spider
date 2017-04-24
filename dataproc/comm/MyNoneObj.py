#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 MyNoneObj.py
# VERSION: 	 1.0
# CREATED: 	 2016-02-08 20:12
# AUTHOR: 	 xuexiang
# DESCRIPTION:   空对象
#
# HISTORY:
#*************************************************************


class MyNoneObj(Exception):

    def __init__(self, msg):
        self.msg = msg

    def __del__(self):
        pass
