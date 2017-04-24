#!/usr/bin/python
#coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 ip_area_server_signal_main.py
# VERSION: 	 1.0
# CREATED: 	 2016-05-26 16:06
# AUTHOR: 	 xuexiang
# DESCRIPTION:   测试单个IP
#
# HISTORY: 
#*************************************************************
import sys
import os
reload(sys)
sys.setdefaultencoding('utf-8')
import comm.PLog
from ip_area_server_class import ip_area_server_class
import redis_conf

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

    # 测试环境
    #data_dir = "E:\\everyday\\20160506\\"

    area = app.get_ip_area_server("223.104.170.121")
    comm.PLog.Log(area)

