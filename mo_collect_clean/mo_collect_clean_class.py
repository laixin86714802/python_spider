#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 mo_collect_clean_class.py
# VERSION: 	 1.0
# CREATED: 	 2016-05-26 14:11
# AUTHOR: 	 xuexiang
# DESCRIPTION:   数据清洗
#                数据采集与业务应用分离。
#                数据清洗的目地仅用于提升有效数据的质量，包括如下方面：
#               (1)丢弃不完整的数据。
#               (2)丢弃并记录异常流量数据。
#               (3)拆分补全非业务字段，如地域和设备信息。
#
#               注：与具体业务应用相应的信息（如product_id、is_comb）则
#               不属于数据清洗范畴。
#
#               当前数据洗清程序主要包括如下内容：
#               (1)丢弃异常格式的数据
#               (2)丢弃必备字段缺失的记录
#               (3)丢弃异常流量数据
#               (4)解析出用户地域信息、设备信息。
# HISTORY:
#*************************************************************
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
import re
import time
import comm.PLog
# import redis_conf
# from ip_area_server_class import ip_area_server_class
from useragent_digger_server_class import useragent_digger_server_class
from DataDropedExcept import DataDropedExcept


class mo_collect_clean_class():
    #**********************************************************************
    # 描  述： 构造函数
    #
    # 返回值：
    # 修  改：
    #**********************************************************************

    def __init__(self):
        # 实例化IP地域解析服务
        #self.m_ip_locate = ip_area_server_class()
        #bRet = self.m_ip_locate.Init(
            #redis_conf.redis_host,
            #redis_conf.redis_port,
            #redis_conf.redis_db,
            #redis_conf.redis_passwd)
        #if not bRet:
            #comm.PLog.Log("服务初始化失败，准备退出!")
            #exit()

        # 实例化UA解析器
        self.m_ua_parser = useragent_digger_server_class()

        # 扫描路径
        # self.m_scan_path = "E:\\everyday\\clean_left"
        self.m_scan_path = "/data/mcontrail"

        # 文件模板
        self.m_file_tmpl = "(?:^mo_\d{8}_\d{4}.src$)"
        # 文件分隔符
        self.m_fld_sep = "$$$"

        # 清洗后数据
        # self.m_outpath = "E:\\everyday\\clean_right"
        self.m_outpath = "/data/DataCenter/mo_wsh_data"

        # 路径不存在则新建路径
        if(not(os.path.exists(self.m_outpath))):
            os.mkdir(self.m_outpath)

        pass

    #**********************************************************************
    # 描  述： 析构函数
    #
    # 返回值：
    # 修  改：
    #**********************************************************************
    def __del__(self):
        pass

    #**********************************************************************
    # 描  述： 主处理函数
    #
    # 参  数：
    #
    # 返回值：
    # 修  改：
    #**********************************************************************
    def do_task(self):

        try:
            # 检测路径
            comm.PLog.Log("扫描路径: %s" % self.m_scan_path)
            dir_exist = os.path.exists(self.m_scan_path)
            if not dir_exist:
                comm.PLog.Log("路径%s不存在" % self.m_scan_path)
                return

            # 扫描新文件: 需要排序，否则入库顺序杂乱
            file_list = sorted(os.listdir(self.m_scan_path))

            for itm in file_list:
                # 检测时间：需要对比文件更新时间与系统时间，保证数据完整
                itm_path = "%s/%s" % (self.m_scan_path, itm)
                update_time = os.stat(itm_path).st_mtime
                now_time = time.time()
                time_diff = (now_time - update_time)
                if time_diff > 30:
                    # 文件名模板非空，则判断
                    if self.m_file_tmpl:
                        re_ftmpl = re.match(self.m_file_tmpl, itm, re.S | re.I)
                        if re_ftmpl is None:
                            continue
                        self.proc_file(itm)

            #一轮结束
            # time.sleep(30)
            # pass
        except:
            pass

    #**********************************************************************
    # 描  述： 处理单个文件
    #
    # 参  数： src_file, 文件名
    #
    # 返回值：
    # 修  改：
    #**********************************************************************
    def proc_file(self, src_file):
        try:
            comm.PLog.Log(
                "====================================================")
            comm.PLog.Log("开始清洗文件：%s" % src_file)

            # src_full_name = "%s\\%s" % (self.m_scan_path, src_file)
            src_full_name = "%s/%s" % (self.m_scan_path, src_file)
            comm.PLog.Log("src_full_name: %s" % src_full_name)

            # 打开文件
            fi = open(src_full_name, "rb")
            out_file_name = re.sub("\.\w+$", ".wsh", src_file)
            # dest_full_name = "%s\\%s" % (self.m_outpath, out_file_name)
            dest_full_name = "%s/%s" % (self.m_outpath, out_file_name)
            fo = open(dest_full_name, "wb")

            eff_cnt = 0
            for line in fi:
                out_line = self.proc_line(line)
                if len(out_line)>0:
                    eff_cnt += 1
                fo.write(out_line)

            # 已经处理结束的文件改名
            comm.PLog.Log("文件清洗结束, 有效行数：%s" % eff_cnt);
            new_src_full_name = re.sub("\.\w+$", ".src.ok", src_full_name)
            comm.PLog.Log(new_src_full_name);
            # 清洗原文件改名
            os.rename(src_full_name, new_src_full_name)

        except:
            #info = sys.exc_info()
            #print info[0], ":", info[1]
            pass

    #**********************************************************************
    # 描  述： 处理文件行
    #
    # 参  数： line_data, 数据行
    #
    # 返回值：
    #   改：
    #**********************************************************************
    def proc_line(self, line_data):
        ret_data = ""

        field_cnt = 11;

        try:
            lst_res = line_data.split(self.m_fld_sep)

            # 当前记录格式
            #
            #AppId,EventType,UserId,UserFlag,PageId,Referrer,Params,IP,UserAgent,time_stamp,human_date

            # 1. 检测字段数量
            if len(lst_res) != field_cnt:
                # 字段格式不正确，丢弃
                raise

            AppId = lst_res[0]
            EventType = lst_res[1]
            UserId = lst_res[2]
            UserFlag = lst_res[3]
            PageId = lst_res[4]
            # Referrer = lst_res[5]
            # Params = lst_res[6]
            HostIP = lst_res[7]
            # UserAgent = lst_res[8]
            TimeStamp = lst_res[9]
            HumanDate = lst_res[10]

            # 检测各个字段的格式
            # AppId是一个数字
            if re.search(r'''^\d+$''', AppId, re.S | re.I ) is None:
                raise DataDropedExcept("AppId failed")

            #EventType是数字
            if re.search(r'''^\d+$''', EventType, re.S | re.I ) is None:
                raise DataDropedExcept("EventType failed")

            # UserId为空、全0的需丢弃***
            if len(UserId) == 0 or re.search(
                    r'''^[0-_]$''', UserId, re.S | re.I ):
                raise DataDropedExcept("UserId failed")

            # UserFlag是0或1
            if re.search(r'''^[01]$''', UserFlag, re.S | re.I ) is None:
                raise DataDropedExcept("UserFlag failed")

            # PageId非空
            if re.search(r'''\w+''', PageId, re.S | re.I ) is None:
                raise DataDropedExcept("PageId failed")

            # HostIP合法性
            if re.search(
                    r'''(?:^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$)''', HostIP, re.S | re.I ) is None:
                raise DataDropedExcept("HostIP failed")

            # TimeStamp合法
            if re.search(r'''\d{13,20}''', TimeStamp, re.S | re.I ) is None:
                raise DataDropedExcept("TimeStamp failed")

            #因2016-6-7日下午18:00升级，对于以前的数据，采用旧表入库，此清洗程序只清洗新数据。 
            if long(TimeStamp) < 1465282848999:
                comm.PLog.Log("旧数据格式，为2016-6-7 18:00以前的数据")
                raise DataDropedExcept("TimeStamp too old, old table ")

            # HumanDate合法
            if re.search(
                    r'''(?:^20\d\d-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}$)''', HumanDate, re.S | re.I ) is None:
                raise DataDropedExcept("HumanDate failed")

            # 获取地域
            #ip_place = self.m_ip_locate.get_ip_area_server(HostIP)
            #prov_name = ""
            #city_name = ""
            #if ip_place:
                #[prov_name, city_name] = ip_place.split(':')

            # 地域信息解析
            #terminal = ""
            #if UserAgent:
                #terminal = self.m_ua_parser.get_terminal_info(UserAgent)

            ################################################################
            ## 格式化输出
            #Params = Params.strip("{} ")

            #if prov_name:
                #if Params:
                    #Params += ","
                #Params += ("'prov_name':'" + prov_name + "'")

            #if city_name:
                #if Params:
                    #Params += ","
                #Params += ("'city_name':'" + city_name + "'")

            #if terminal:
                #if Params:
                    #Params += ","
                #Params += ("'terminal':'" + terminal + "'")

            #other_params = ("{" + Params + "}")

            ## 输出: 仅需替换other_params参数
            #lst_res[6] = other_params



            ret_data = "$$$".join(lst_res)

        except DataDropedExcept as ex:
            #comm.PLog.Log("丢弃, ex=%s" % ex.msg)
            ret_data = ""
        except:
            #info = sys.exc_info()
            # print info[0], ":", info[1]
            pass

        return ret_data

