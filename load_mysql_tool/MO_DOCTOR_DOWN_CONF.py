#!/usr/bin/python
#coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 MO_DOCTOR_DOWN_CONF.py
# VERSION: 	 1.0
# CREATED: 	 2016-05-11 13:30
# AUTHOR: 	 xuexiang
# DESCRIPTION:   掌上医生加载入库配置
#
# HISTORY: 
#*************************************************************

# 轮询检测周期(分钟)
SCAN_CIRCLE = 10

# 入库文件路径
LOAD_FILE_PATH = "/data/developer/apps/DataAnalyse/StatLog"
#LOAD_FILE_PATH = "E:/everyday/20160511/stat"


# 入库文件模板
LOAD_FILE_TMPL = "MO_DOCTOR_DOWN_\d{8}\.stat"

# 目标表
TARGET_TABLE = "shw_mo_doctor_down"

# 字段分隔符
FIELD_SEPARATOR = '$$$'

# 目标表结构
FIELD_LIST = "collect_date, float_ask, float_news, float_jibing, wechat_jkwz, wechat_fk, wechat_wz, wechat_dxsy, wechat_fkzx, wechat_nkzx, wechat_xb, wechat_ynxj, from_home, from_ask, imm_down, confirm_down"

# 改名, 为空则不执行改名
LOAD_RENAME = ".load.ok"

# 是否压缩备份
IS_ZIP = False
ZIP_PATH = ""
