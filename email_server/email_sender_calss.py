#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 email_sender_calss.py
# VERSION: 	 1.0
# CREATED: 	 2016-02-02 16:54
# AUTHOR: 	 xuexiang
# DESCRIPTION:   Email服务器
#
# HISTORY:
#*************************************************************

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import time
from db_helper import db_helper_class
import smtplib
from email.mime.text import MIMEText
import PLog

import conf.db_conf
import comm.PLog

import conf.app_conf
import conf.class_conf
import conf.db_conf
from comm.db_helper import db_helper_class


class email_sender_calss():

    def __init__(self):
        self.db_oper = db_helper_class(conf.db_conf)

    def __del__(self):
        pass

    def do_task(self):
        self.send_email()
        pass

    def get_content(self):
        str_content = ""
 
        #没有完成的应用告警
        sql = r'''
            select * from 
            (
            select a.nAppId as app_id, a.nClassId as class_id, b.sClassName as class_name, count(*) as job_complated_cnt
            from man_job_report_stat a, bas_class_conf b 
            where a.nClassId = b.nClassId and a.sInsertTime like '2016-02-24%' and a.sState='complate'
            group by a.nAppId, a.nClassId
            ) a 
            where job_complated_cnt =0;
        '''
        #sql = "select b.sClassName, sJobId, nAllTaskCnt, nNormalCnt, nDownFailedCnt, \
               #nParseFailedCnt, nOtherFailedCnt, fSucessRate, sJobStartTime,  \
               #sJobEndTime, sState \
               #from man_job_report_stat a, bas_class_conf b \
                #where a.nClassId = b.nClassId and a.sInsertTime like '2016-02-24%'"

        (line_cnt, data_set) = self.db_oper.exe_search(sql)
        str_content = "告警数量：<h3>%d</h3> \n" % line_cnt
        #for data_row in data_set:
            #app_id = data_row["app_id"]
            #class_id = data_row["class_id"]
            #class_name = data_row["class_name"]
            #job_complated_cnt = data_row["job_complated_cnt"]

        return str_content
         

    def send_email(self):
        sender = 'xzq0102@126.com'
        receiver = 'xuexiang'

        curr_time = time.strftime("%Y-%m-%d %H:%M:%S")
        subject = '大数据采集运行报告 %s' % (curr_time)

        smtpserver = 'smtp.126.com'
        username = 'xzq0102@126.com'
        password = '123456'

        str_body= self.get_content()
        str_html = "<html><h1>大数据采集系统运行状态如下:</h1><br>%s</html>" % str_body

        msg = MIMEText(str_html, 'html', 'utf-8')
        msg['Subject'] = subject

        smtp = smtplib.SMTP(smtpserver)
        # smtp.connect(smtpserver)

        #smtp.esmtp_features["auth"]="LOGIN PLAIN"
        # smtp.esmtp_features["auth"]="LOGIN"
        smtp.esmtp_features["auth"] = "PLAIN"
        (code, resp) = smtp.login(username, password)
        #PLog.Log("code=%d, resp=%s " % (code, resp))
        if 0:
            # if code != 235:
            PLog.Log("登录邮件服务器失败.")
        else:
            PLog.Log("登录邮件服务器成功.")
            result = smtp.sendmail(sender, receiver, msg.as_string())
            print result
            smtp.quit()
        pass
