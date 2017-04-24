#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 product_thumb_image_server_class.py
# VERSION: 	 1.0
# CREATED: 	 2016-05-20 10:32
# AUTHOR: 	 xuexiang
# DESCRIPTION:   产品图片服务服务
#
# HISTORY:
#*************************************************************
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
import re
import time
import urllib2
import cookielib
import comm.PLog
import conf.db_conf
from comm.db_helper import db_helper_class


class product_thumb_image_server_class():

    def __init__(self):
        # 图片保存路径
        self.m_save_root = ""
        # 分页大小
        self.page_size = 20
        # 偏移大小
        self.off_size = 0

        self.m_db_oper = db_helper_class(conf.db_conf)

        pass

    def __del__(self):
        pass

    def init(self, save_path):
        bRet = True

        self.m_save_root = save_path
        self.mkdir(self.m_save_root)
        comm.PLog.Log("图片存储服务路径: %s" % self.m_save_root)

        try:
            self.service()
        except:
            bRet = False
        finally:
            pass

        return bRet

    def service(self):

        while True:
            # 从数据库分页读取数据
            sql = "select app_type, image_id, image_url, collect_time " \
            "from wrk_thumb_image_down where down_state is null or down_state=0 limit %d offset %d" % (
                self.page_size, self.off_size)

            self.off_size += self.page_size
            (line_cnt, tbl_datas) = self.m_db_oper.exe_search(sql)

            if line_cnt == 0:
                comm.PLog.Log("所有图均已经下载.")
                return

            for row_data in tbl_datas:
                try:
                    comm.PLog.Log(
                        "===============================================")
                    fld_app_type = row_data["app_type"]
                    fld_image_id = row_data["image_id"]
                    fld_image_url = row_data["image_url"]
                    fld_collect_time = str(row_data["collect_time"])

                    fld_app_type = fld_app_type.strip()
                    if len(fld_collect_time) < 8:
                        continue

                    # 2016-05
                    fld_collect_time = fld_collect_time[0:7]

                    comm.PLog.Log("图片标识: %s " % fld_image_id)
                    comm.PLog.Log("图片地址: %s" % fld_image_url)

                    self.req_thumb_image(
                        fld_app_type,
                        fld_image_id,
                        fld_image_url,
                        fld_collect_time)
                except:
                    pass

    def req_thumb_image(self, app_type, product_id, image_url, collect_time):
        try_count = 0
        max_retry = 3
        try:
            comm.PLog.Log("开始下载图片")
            try_count += 1
            cj = cookielib.LWPCookieJar()
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
            urllib2.install_opener(opener)

            # URL适配
            if image_url.startswith("//"):
                image_url = "http:" + image_url

            image_url = image_url.strip()
            if len(image_url) == 0:
                sql = "update wrk_thumb_image_down set down_state=-1 where image_id=%s" % product_id
                self.m_db_oper.exe_update(sql)
                return

            comm.PLog.Log("图片地址：%s" % image_url)

            req = urllib2.Request(image_url)
            operate = opener.open(req)
            data = operate.read()
            if data:
                comm.PLog.Log("save")
                # 获取图片成功，保存
                full_path_dir = self.m_save_root + "/" + app_type + "/" + collect_time
                self.mkdir(full_path_dir)

                #图片的相对路径
                image_full_name=  app_type + "/" + collect_time + "/" + product_id + ".png"
                comm.PLog.Log("image_full_name=%s" % image_full_name)

                image_full_path =  self.m_save_root + "/" + image_full_name
                fobj = open(image_full_path, "wb")
                fobj.write(data)
                fobj.flush()
                fobj.close()

                # 已经下载成功的图处，从redis中删除
                comm.PLog.Log("产品%s图片获取成功!" % product_id)

                # 更新数据库
                sql = "update wrk_thumb_image_down set down_state=1, image_name='%s' where image_id=%s" % (image_full_name, product_id)
                self.m_db_oper.exe_update(sql)
                return
            else:
                if try_count >= max_retry:
                    sql = "update wrk_thumb_image_down set down_state=-1 where image_id=%s" % product_id
                    self.m_db_oper.exe_update(sql)
                    return
        except:
            raise
            if try_count >= max_retry:
                sql = "update wrk_thumb_image_down set down_state=-1 where image_id=%s" % product_id
                self.m_db_oper.exe_update(sql)
                return
            pass

    #**********************************************************************
    # 描  述： 检测并创建本地目录
    #
    # 参  数： path, 路径
    #
    # 返回值： 返回路径
    # 修  改：
    #**********************************************************************
    def mkdir(self, path):
        # 去除两边的空格
        path = path.strip()
        # 去除尾部的\符号
        path = path.rstrip("\\")

        if not os.path.exists(path):
            os.makedirs(path)

        return path
