#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 DataDropedExcept.py
# VERSION: 	 1.0
# CREATED: 	 2016-02-08 19:50
# AUTHOR: 	 xuexiang
# DESCRIPTION:   清洗丢弃
#
# HISTORY:
#*************************************************************


class DataDropedExcept(Exception):

    def __init__(self, msg=''):
        self.msg = msg

    def __del__(self):
        pass
