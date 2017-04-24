#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME:      db_helper.py
# VERSION:   1.0
# CREATED:   2016-12-22 17:53:17
# AUTHOR:    xuexiang
# DESCRIPTION:   低价集中类
#
# HISTORY:
#*************************************************************
from comm.mysql_helper import mysql_helper_class
import conf.db_conf
import time

class low_price_focus(object):
    """低价集中类"""
    def __init__(self):
        # MySQL20数据库对象
        self.mysql_db_oper = mysql_helper_class(conf.db_conf)
    def get_low_price_focus(self):
        '''获取低价集中数据'''
        sql_low_price_focus = '''SELECT A.date_time, M.count, count(*) as 'all_count', M.count / count(*) as 'low_price_num_per'
            FROM tb_deloitte_low_price_num_pretreatment as A,
            (SELECT date_time, count(*) as count FROM tb_deloitte_low_price_num_pretreatment
            WHERE jk_low_price = 1 
            GROUP BY date_time) as M
            WHERE A.date_time = M.date_time
            GROUP BY A.date_time '''
        data_item = {}
        (line_low_price_focus, res_low_price_focus) = self.mysql_db_oper.exe_search(sql_low_price_focus)
        for low_price_focus in res_low_price_focus:
            data_item['date_time'] = low_price_focus['date_time']
            data_item['jk_low_price_num'] = low_price_focus['count']
            data_item['all_count'] = low_price_focus['all_count']
            data_item['low_price_num_per'] = low_price_focus['low_price_num_per']
            self.load_to_db(data_item)

    def load_to_db(self, data_item):
        '''入库函数'''
        collecttime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(time.time())))
        sql = '''INSERT INTO tb_shw_dt_lowprice_num_mon(date_time, jk_low_price_num, all_count, low_price_num_per, collect_time) 
                VALUES(%s, %s, %s, %s, %s)'''
        vals = (
            data_item['date_time'],
            data_item['jk_low_price_num'],
            data_item['all_count'],
            data_item['low_price_num_per'],
            collecttime
            )
        self.mysql_db_oper.exe_insert(sql, vals)
        print "["+collecttime+"]", u"入库成功."

a = low_price_focus()
a.get_low_price_focus()