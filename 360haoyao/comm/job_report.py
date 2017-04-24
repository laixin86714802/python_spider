#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 job_report.py
# VERSION: 	 1.0
# CREATED: 	 2016-02-23 11:37
# AUTHOR: 	 xuexiang
# DESCRIPTION:   作业状态上报
#
# HISTORY:       WLT 2016-02-23 V1.0
#                    创建此基础库.
#
#*************************************************************
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import time


#**********************************************************************
# 描  述： 初始化job report
#
# 参  数： app_id0, 应用标识
# 参  数： class_id0, 类别标识
# 参  数： job_id0, job标识
# 参  数： all_task_cnt, 总任务量
# 参  数： db_oper0, 数据库对象
#
# 返回值： 成功True, 失败false
# 修  改：
#**********************************************************************
def report_start(app_id0, class_id0, job_id0,
                 all_task_cnt, db_oper0, remark0=""):
    ret_value = True

    try:
        sCurrTime = time.strftime("%Y-%m-%d %H:%M:%S")

        sql = "insert into man_job_report_stat(nAppId, nClassId, sJobId, nAllTaskCnt, \
                sJobStartTime, sState, sInsertTime, sRemark ) \
                values(%s, %s, %s, %s, %s, %s, %s, %s)"
        value = (app_id0,
                 class_id0,
                 job_id0,
                 all_task_cnt,
                 sCurrTime,
                 "doing",
                 sCurrTime,
                 remark0)
        db_oper0.exe_insert(sql, value)
    except:
        ret_value = False
        pass

    return ret_value


#**********************************************************************
# 描  述： job完成报告
#
# 参  数： job_id0, Job标识
# 参  数： job_stat0, job统计数据
# 参  数： db_oper0, 数据库对象
# 参  数： remark0, 注释
#
# 返回值：
# 修  改：
#**********************************************************************
def report_finish(job_id0, job_stat0, db_oper0, remark0=""):
    ret_value = True

    try:
        sCurrTime = time.strftime("%Y-%m-%d %H:%M:%S")

        fRate = "%.2f" % (job_stat0.down_ok_count /
                          float(job_stat0.all_task_count))

        sql = "update man_job_report_stat set nNormalCnt=%s, \
                nDownFailedCnt=%s, nParseFailedCnt=%s, nOtherFailedCnt=%s, \
                fSucessRate=%s, sState='%s', sJobEndTime='%s', sInsertTime='%s', sRemark='%s' \
                where sJobId='%s'" % (job_stat0.down_ok_count,
                                      job_stat0.down_failed_count,
                                      job_stat0.parse_failed_count,
                                      job_stat0.other_failed_count,
                                      fRate,
                                      "complate",
                                      sCurrTime,
                                      sCurrTime,
                                      remark0,
                                      job_id0)
        db_oper0.exe_update(sql)
    except:
        ret_value = False
        pass

    return ret_value
