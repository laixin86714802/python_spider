#!/usr/bin/python
#coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 test3.py
# VERSION: 	 1.0
# CREATED: 	 2016-02-02 18:02
# AUTHOR: 	 xuexiang
# DESCRIPTION: 
#
# HISTORY: 
#*************************************************************
import smtplib

sender = 'xiongzhenqian@jianke.com'
receivers = ['xzq0102@163.com']

message = """From: From Person <from@fromdomain.com>
To: To Person <to@todomain.com>
Subject: SMTP e-mail test

This is a test e-mail message.
"""

smtpObj = smtplib.SMTP('172.16.240.16')
smtpObj.sendmail(sender, receivers, message)         
print "Successfully sent email"
