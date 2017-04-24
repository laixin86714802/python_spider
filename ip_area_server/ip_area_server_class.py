#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 ip_area_server_class.py
# VERSION: 	 1.0
# CREATED: 	 2016-05-06 18:02
# AUTHOR: 	 xuexiang
# DESCRIPTION:   IP地域分布解析
#
# HISTORY:
#*************************************************************
import redis
import re
import xml.dom.minidom
import time
import comm.PLog
import comm.requests_pkg
import comm.stone_funs
import sys
import os
reload(sys)
sys.setdefaultencoding('utf-8')


class ip_area_server_class():

    def __init__(self):
        # redis数据库连接
        self.m_redis_conn = None
        # 省份列表
        self.m_province_arr = []
        # 城市列表
        self.m_city_arr = []
        # 一个源文件中的IP列表
        self.m_ip_set = set([])

    def __del__(self):
        pass

    #**********************************************************************
    # 描  述： 初始化服务
    #
    # 参  数： redis_host, redis数据库主机
    # 参  数： redis_port, redis端口
    # 参  数： redis_db_id, redis数据库序号
    # 参  数： password, 鉴权
    #
    # 返回值： 成功True, 失败False
    # 修  改：
    #**********************************************************************
    def Init(self, redis_host, redis_port, redis_db_id=0, password=''):
        bRet = True

        try:
            self.m_redis_conn = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db_id,
                password=password)
            if self.m_redis_conn.ping():
                comm.PLog.Log("连接redis成功")

                domTree = xml.dom.minidom.parse("AreaCode.xml")
                collection = domTree.documentElement

                #<class 'xml.dom.minicompat.NodeList'>
                prov_node_list = collection.getElementsByTagName("Province")
                for prov in prov_node_list:
                    # 添加到省份列表
                    self.m_province_arr.append(prov.getAttribute('name'))
                    city_node_list = prov.getElementsByTagName('item')
                    for city in city_node_list:
                        # 添加到城市列表
                        self.m_city_arr.append(city.getAttribute('name'))
        except:
            bRet = False
        finally:
            pass

        return bRet

    #**********************************************************************
    # 描  述： 批量请求分析
    #
    # 参  数： data_src_file,源数据文件, 指JAVA WEB输出的数据文件
    #          mo_20160507_0800.src
    #          pc_20160507_0800.src
    #
    # 返回值： 空
    # 修  改：
    #**********************************************************************
    def do_bat_requests(self, data_src_file):
        re_src_file = re.search(
            r'''\w{2}_\d{8}_\d{2}00\.src''',
            data_src_file,
            re.S | re.I)
        if re_src_file == None:
            comm.PLog.Log("输入文件%s不是src文件, 丢弃!" % data_src_file)
            return

        self.get_uniq_ipset(data_src_file)

        for ip in self.m_ip_set:
            self.get_ip_area_server(ip)

    #**********************************************************************
    # 描  述：处理已经进行IP去重提纯的Ip数据文件
    #         此函数一般用于处理历史数据
    #
    # 参  数：ip_uniq_file, IP数据文件
    #
    # 返回值：空
    # 修  改：
    #**********************************************************************
    def do_ip_uniq_file_equest(self, ip_uniq_file):
        fi = open(ip_uniq_file, 'r')
        if not os.path.exists(ip_uniq_file):
            comm.PLog.Log("文件%s不存在!" % ip_uniq_file)

        while True:
            line = fi.readline()
            if not line:
                break

            ip = line.strip()
            self.get_ip_area_server(ip)

    #**********************************************************************
    # 描  述： 获取指定的源数据文件中，ip集合
    #
    # 参  数： data_src_file, 源数据文件
    #
    # 返回值： 返回PV
    # 修  改：
    #**********************************************************************
    def get_uniq_ipset(self, data_src_file):
        uniq_ip_cnt = 0

        try:
            fi = open(data_src_file, 'r')
            comm.PLog.Log("当前数据文件名 %s" % data_src_file)

            while True:
                line = fi.readline()
                if not line:
                    break

                line = line.strip()
                line_arr = line.split('$$$')
                if len(line_arr) > 3:
                    ip = line_arr[3]
                    if ip:
                        # 对IP进行合法性检测
                        #^\d{1,3}.\d{1,3}\.\d{1,3}\.\d{1,3}$
                        re_ip = re.search(
                            r'''^\d{1,3}.\d{1,3}\.\d{1,3}\.\d{1,3}$''', ip, re.S | re.I )
                        if re_ip == None:
                            # 丢弃
                            continue
                        self.m_ip_set.add(ip)
                        uniq_ip_cnt += 1

            fi.close()
        except:
            pass

        comm.PLog.Log("源文件%s中的uniq ip数量为：%d" % (data_src_file, uniq_ip_cnt))
        return uniq_ip_cnt

    #**********************************************************************
    # 描  述： 判断IP是否已经存在redis数据库中
    #
    # 参  数： ip, 待分析的IP地址
    #
    # 返回值： 存在true, 否则false
    # 修  改：
    #**********************************************************************
    def exist_in_redis(self, ip_seg):
        ret = self.m_redis_conn.get(ip_seg)
        if ret == None:
            return False

        return True

    #**********************************************************************
    # 描  述： 获取IP服务
    #
    # 参  数： ip, IP地址
    #
    # 返回值： "省:市"
    # 修  改： 
    #**********************************************************************
    def get_ip_area_server(self, ip): 
        ret_info = ""

        ip = ip.strip()
        if ip:
            # 对IP进行合法性检测
            re_ip = re.search(
                r'''^\d{1,3}.\d{1,3}\.\d{1,3}\.\d{1,3}$''', ip, re.S | re.I )
            if re_ip == None:
                # 丢弃
                return ""

            # 服务请求
            id_dot = ip.rindex(".")
            ip_seg = ip[0:id_dot]
            ret_info = self.m_redis_conn.get(ip_seg)
            if ret_info == None:
                #即时请求
                comm.PLog.Log("============================================")
                comm.PLog.Log("%s不存在于redis，请求sina" % ip_seg)
                ret_info = self.ip_area_request(ip)
            else:
                comm.PLog.Log("%s已经存在" % ip_seg)

        return ret_info

    #**********************************************************************
    # 描  述： 获取IP的地址
    #
    # 参  数： ip, 待请求的IP地址
    #
    # 返回值：
    # 修  改：
    #**********************************************************************
    def ip_area_request(self, ip):
        url = 'http://int.dpool.sina.com.cn/iplookup/iplookup.php?ip=' + ip
        (http_ok, resp) = comm.requests_pkg.get(url)

        #返回信息
        return_info = ""

        if http_ok:
            #------------------------------------------------------------------
            # 作  者： wltsoft
            # 时  间： 2016-05-06 18:15
            # 备注头： 新浪返回数据样式说明
            # 备注体： 返回数据样式：
            #           1	-1	-1	中国	北京	北京
            #           1	-1	-1	美国	纽约州	Brooklyn
            #           1	-1	-1	中国	湖南
            #           1 -1      -1      澳大利亚        South Australia Adelaide
            #           1 -1      -1      澳大利亚        维多利亚        Yundool
            #           1 -1      -1      中国    台湾
            #           1 -1      -1      中国    河北    邢台
            #
            #------------------------------------------------------------------
            #resp_content = comm.stone_funs.ToUtf8(resp.content)

            resp_content = resp.content.decode('GB2312', 'ignore')
            resp_content = resp_content.strip()
            comm.PLog.Log("resp_content: " + resp_content)

            addr_list = re.split(r'\s+', resp_content)
            comm.PLog.Log(resp_content)

            if len(addr_list) > 5:
                prov_name = addr_list[4]
                city_name = addr_list[5]

                # 判断是否为国内, 对于国外：国家名-州名
                pattern = unicode('中国', 'utf-8')
                re_china = re.search(pattern, resp_content, re.S | re.I)
                if re_china == None:
                    prov_name = addr_list[3]
                    city_name = addr_list[4]

                fmt_prov_name = self.fmt_area_info(
                    self.m_province_arr, prov_name)
                fmt_city_name = self.fmt_area_info(self.m_city_arr, city_name)

                # 优先取适配数据，取不到则取原数据
                if fmt_prov_name == '':
                    fmt_prov_name = prov_name
                    fmt_city_name = city_name

                self.save(ip, fmt_prov_name, fmt_city_name)
                return_info = '%s:%s' % (prov_name, city_name)
            elif len(addr_list) == 5:
                prov_name = addr_list[4]

                fmt_prov_name = self.fmt_area_info(
                    self.m_province_arr, prov_name)

                self.save(ip, fmt_prov_name, "")
                return_info = '%s:%s' % (fmt_prov_name, "")
            elif len(addr_list) == 4:
                self.save(ip, "", "")
            else:
                comm.PLog.Log("ip match failed")
        else:
            comm.PLog.Log("ip %s 请求失败,放弃!" % ip)

        return return_info


    #**********************************************************************
    # 描  述： 匹配地域信息
    #
    # 参  数： arr, 匹配基础数据
    # 参  数： val, 待匹配项
    #
    # 返回值： 匹配后的信息，即省份名或地市名
    # 修  改：
    #**********************************************************************
    def fmt_area_info(self, arr, val):
        ret_fmt_info = ""

        try:
            #要求非空
            if val:
                for item in arr:
                    if item == val:
                        ret_fmt_info = val
                        break

                    if re.match(val, item):
                        ret_fmt_info = item
                        break
        except:
            pass

        return ret_fmt_info

    #**********************************************************************
    # 描  述： 保存解析出来的地址信息
    #
    # 参  数： prov_name, 省份名
    # 参  数： city_name, 地市名
    #
    # 返回值： 空
    # 修  改：
    #**********************************************************************
    def save(self, ip, prov_name, city_name):
        if prov_name != "":
            addr_mark = '%s:%s' % (prov_name, city_name)
            id_dot = ip.rindex(".")
            ip_seg = ip[0:id_dot]
            # 省份和地市均空的，不要写缓存
            self.m_redis_conn.set(ip_seg, addr_mark)

        # 写IP天文件
        IpLogPath = "./IPLog"
        if not os.path.exists(IpLogPath):
            os.mkdir(IpLogPath)

        addr_full_info = "%s:%s:%s" % (
            ip, prov_name, city_name)
        comm.PLog.Log(addr_full_info)

        curr_time = time.strftime('%Y%m%d', time.localtime(int(time.time())))
        fo_name = "%s/IPAREA_%s.dat" % (IpLogPath, curr_time)
        fo = open(fo_name, 'a')
        fo.write(addr_full_info + "\n")
