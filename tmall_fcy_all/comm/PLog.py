#!/usr/bin/python
#coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 PLog.py
# VERSION: 	 1.0
# CREATED: 	 2016-01-12 13:59
# AUTHOR: 	 xuexiang
# DESCRIPTION:   自定义日志类
#
# HISTORY: 
#*************************************************************
import time

def Log(content):
    fo = open("./runtime.log", "ab")
    currtm = time.strftime('[%Y-%m-%d %H:%M:%S]',
                           time.localtime(int(time.time())))
    print >>fo, currtm, content
    fo.flush()

    print "%s %s" %(currtm, content.decode("utf-8", "ignore").encode("gbk", "ignore"))

def Except(content):
    fo = open("./runtime.log", "ab")
    currtm = time.strftime('[%Y-%m-%d %H:%M:%S]',
                           time.localtime(int(time.time())))
    print >>fo, currtm, "[Except]", content
    fo.flush()

    print "%s %s %s" %(currtm, "[Except]", content.decode("utf-8", "ignore").encode("gbk", "ignore"))

def TempLog(fname, content):
    fo = open(fname, "wb")
    print >> fo, content
    fo.flush()

