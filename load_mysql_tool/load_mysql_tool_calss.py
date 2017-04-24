#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 load_mysql_tool_calss.py
# VERSION: 	 1.0
# CREATED: 	 2016-05-11 11:03
# AUTHOR: 	 xuexiang
# DESCRIPTION:
#
# HISTORY:
#*************************************************************
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
import re
import time
import comm.PLog
import buz_db_conf
from comm.db_helper import db_helper_class
import MO_DETAIL_CONF
import MO_DOCTOR_DOWN_CONF
import MO_MALL_DOWN_CONF
import MO_HEALTH_NEWS_CONF


class load_mysql_tool_calss:

    def __init__(self):
        # 扫描路径
        self.m_scan_path = ""
        # 文件模板
        self.m_file_tmpl = ""
        # 文件分隔符
        self.m_fld_sep = ""
        # 目标表
        self.m_target_table = ""
        # 字段列表
        self.m_fld_list = ""
        # 改名模板
        self.m_load_rename = ""
        # 是否ZIP
        self.m_iszip = False
        # ZIP路径
        self.m_zip_path = ""

        # 字段数量
        self.m_flds_count = 0

        # 数据库连接
        self.db_oper = db_helper_class(buz_db_conf)

    def __del__(self):
        pass

    def do_main(self):
        try:
            # 加载MO_DETAIL
            self.load_conf("MO_DETAIL")
            self.load_app()

            # 加载MO_DOCTOR_DOWN
            self.load_conf("MO_DOCTOR_DOWN")
            self.load_app()

            # 加载MO_MALL_DOWN
            self.load_conf("MO_MALL_DOWN")
            self.load_app()

            # 加载MO_HEALTH_NEWS
            self.load_conf("MO_HEALTH_NEWS")
            self.load_app()

            # 休眠10分钟
            # time.sleep(60 * 10)
        except:
            pass

    #**********************************************************************
    # 描  述： 清理配置
    #
    # 返回值： 空
    # 修  改：
    #**********************************************************************
    def clear_conf(self):
        self.m_scan_path = ""
        self.m_file_tmpl = ""
        self.m_fld_sep = ""
        self.m_target_table = ""
        self.m_fld_list = ""
        self.m_load_rename = ""
        self.m_iszip = False
        self.m_zip_path = ""
        self.m_flds_count = 0

    #**********************************************************************
    # 描  述： 加载配置项
    #
    # 参  数： app_name, 加载应用名称
    #
    # 返回值： 空
    # 修  改：
    #**********************************************************************
    def load_conf(self, app_name):
        self.clear_conf()

        if app_name == "MO_DETAIL":
            self.m_scan_path = MO_DETAIL_CONF.LOAD_FILE_PATH
            self.m_file_tmpl = MO_DETAIL_CONF.LOAD_FILE_TMPL
            self.m_fld_sep = MO_DETAIL_CONF.FIELD_SEPARATOR
            self.m_target_table = MO_DETAIL_CONF.TARGET_TABLE
            self.m_fld_list = MO_DETAIL_CONF.FIELD_LIST
            self.m_load_rename = MO_DETAIL_CONF.LOAD_RENAME
            self.m_iszip = MO_DETAIL_CONF.IS_ZIP
            self.m_zip_path = MO_DETAIL_CONF.ZIP_PATH
        elif app_name == "MO_DOCTOR_DOWN":
            self.m_scan_path = MO_DOCTOR_DOWN_CONF.LOAD_FILE_PATH
            self.m_file_tmpl = MO_DOCTOR_DOWN_CONF.LOAD_FILE_TMPL
            self.m_fld_sep = MO_DOCTOR_DOWN_CONF.FIELD_SEPARATOR
            self.m_target_table = MO_DOCTOR_DOWN_CONF.TARGET_TABLE
            self.m_fld_list = MO_DOCTOR_DOWN_CONF.FIELD_LIST
            self.m_load_rename = MO_DOCTOR_DOWN_CONF.LOAD_RENAME
            self.m_iszip = MO_DOCTOR_DOWN_CONF.IS_ZIP
            self.m_zip_path = MO_DOCTOR_DOWN_CONF.ZIP_PATH
        elif app_name == "MO_MALL_DOWN":
            self.m_scan_path = MO_MALL_DOWN_CONF.LOAD_FILE_PATH
            self.m_file_tmpl = MO_MALL_DOWN_CONF.LOAD_FILE_TMPL
            self.m_fld_sep = MO_MALL_DOWN_CONF.FIELD_SEPARATOR
            self.m_target_table = MO_MALL_DOWN_CONF.TARGET_TABLE
            self.m_fld_list = MO_MALL_DOWN_CONF.FIELD_LIST
            self.m_load_rename = MO_MALL_DOWN_CONF.LOAD_RENAME
            self.m_iszip = MO_MALL_DOWN_CONF.IS_ZIP
            self.m_zip_path = MO_MALL_DOWN_CONF.ZIP_PATH
        elif app_name == "MO_HEALTH_NEWS":
            self.m_scan_path = MO_HEALTH_NEWS_CONF.LOAD_FILE_PATH
            self.m_file_tmpl = MO_HEALTH_NEWS_CONF.LOAD_FILE_TMPL
            self.m_fld_sep = MO_HEALTH_NEWS_CONF.FIELD_SEPARATOR
            self.m_target_table = MO_HEALTH_NEWS_CONF.TARGET_TABLE
            self.m_fld_list = MO_HEALTH_NEWS_CONF.FIELD_LIST
            self.m_load_rename = MO_HEALTH_NEWS_CONF.LOAD_RENAME
            self.m_iszip = MO_HEALTH_NEWS_CONF.IS_ZIP
            self.m_zip_path = MO_HEALTH_NEWS_CONF.ZIP_PATH

    def load_app(self):
        # 检测路径
        comm.PLog.Log("扫描路径: %s" % self.m_scan_path)
        dir_exist = os.path.exists(self.m_scan_path)
        if not dir_exist:
            comm.PLog.Log("路径%s不存在", self.m_scan_path)
            return

        # 字段解析
        fld_arr = self.m_fld_list.split(",")
        self.m_flds_count = len(fld_arr)
        comm.PLog.Log("字段数量: %d" % self.m_flds_count)

        # 扫描新文件: 需要排序，否则入库顺序杂乱
        file_list = sorted(os.listdir(self.m_scan_path))

        for itm in file_list:
            # 文件名模板非空，则判断
            if self.m_file_tmpl:
                re_ftmpl = re.match(self.m_file_tmpl, itm, re.S | re.I)
                if re_ftmpl is None:
                    continue
                self.proc_file(itm)

    #**********************************************************************
    # 描  述：处理一个文件
    #
    # 参  数：src_file, 待入库文件名
    #
    # 返回值：空
    # 修  改：
    #**********************************************************************
    def proc_file(self, src_file):
        try:
            comm.PLog.Log(
                "====================================================")
            comm.PLog.Log("处理文件：%s" % src_file)
            file_full_name = "%s/%s" % (self.m_scan_path, src_file)
            comm.PLog.Log("file_full_name: %s" % file_full_name)

            # 批量入库
            sql = "load data local infile '%s' into table %s charset utf8  FIELDS TERMINATED BY '%s' (%s)" % (
                file_full_name, self.m_target_table, self.m_fld_sep, self.m_fld_list)
            self.db_oper.exe_update(sql)

            # 改名
            if self.m_load_rename.strip():
                comm.PLog.Log("改名...")
                new_full_name = re.sub("\.\w+$", self.m_load_rename, file_full_name)
                os.rename(file_full_name, new_full_name)
        except:
            pass
