#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 requests_pkg.py
# VERSION: 	 1.0
# CREATED: 	 2016-01-14 20:25
# AUTHOR: 	 xuexiang
# DESCRIPTION:   requests类的包裹器
#
# HISTORY:
#*************************************************************
import time
import requests
from random_useragent import getRandomUA


def get(url, max_try=3, timeout=100):
    try_count = 0
    while True:
        h_heads = getRandomUA()
        resp = requests.get(url, headers=h_heads, timeout=timeout)
        try_count += 1
        if resp:
            return resp
        else:
            if try_count >= max_try:
                return None
            time.sleep(3)
