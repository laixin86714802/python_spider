#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 ttt.py
# VERSION: 	 1.0
# CREATED: 	 2016-05-18 14:57
# AUTHOR: 	 xuexiang
# DESCRIPTION:
#
# HISTORY:
#*************************************************************
import sys
import requests
import time


def get(url, max_try=3, timeout=20):

    try:
        resp = requests.get(url, timeout=timeout)
        print resp.status_code
        print type(resp)
        print resp

        if resp == None:
            print "11"
        else:
            print "22"

        if resp is None:
            print "33"
        else:
            print "44"

        if resp:
            print "55"
            return resp

    except:
        info = sys.exc_info()
        print info[0], ":", info[1]

        pass

if __name__ == '__main__':
    url = "http://www.jianke.com/error2.html"
    get(url, 0)
