#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 ip_area_server_uniqfile_main.py
# VERSION: 	 1.0
# CREATED: 	 2016-05-06 18:03
# AUTHOR: 	 xuexiang
# DESCRIPTION:
#
# HISTORY:
#*************************************************************
import sys
import os
reload(sys)
sys.setdefaultencoding('utf-8')
import comm.PLog
import redis_conf
from ip_area_server_class import ip_area_server_class

if __name__ == '__main__':
    app = ip_area_server_class()
    bRet = app.Init(
        redis_conf.redis_host,
        redis_conf.redis_port,
        redis_conf.redis_db,
        redis_conf.redis_passwd)

    if not bRet:
        comm.PLog.Log("服务初始化失败，准备退出!")
        exit()

    uniq_file = "E:\\everyday\\20160507\\ip_all.dat";
    #uniq_file = ""
    app.do_ip_uniq_file_equest(uniq_file)
