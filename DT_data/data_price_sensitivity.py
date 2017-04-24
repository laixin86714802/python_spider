#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME:      db_helper.py
# VERSION:   1.0
# CREATED:   2016-12-21 16:51:11
# AUTHOR:    xuexiang
# DESCRIPTION:   数据入库类
#
# HISTORY:
#*************************************************************
from comm.mysql_helper import mysql_helper_class
import conf.db_conf
import time

class price_sensitivity(object):
    """指标五：价格敏感度"""
    def __init__(self):
        # MySQL20数据库对象
        self.mysql_db_oper = mysql_helper_class(conf.db_conf)
    def get_prod_id(self):
        '''获取价格敏感度'''
        # 获取商品id
        sql_prod_id = '''SELECT prod_id FROM `tb_deloitte_price_sensitive_pretreatment` GROUP BY prod_id'''
        (line_prod_id, res_prod_id) = self.mysql_db_oper.exe_search(sql_prod_id)
        if res_prod_id:
            for prod_id in res_prod_id:
                sql_price_sensitivity = '''SELECT A.prod_id, M.last_price as 'last_price', A.last_price as 'now_price', 
                    M.average_sales_volume as 'last_price_ave', A.average_sales_volume as 'now_price_ave', 
                    M.diff_days as 'last_price_days', A.diff_days as 'now_price_days',
                    (M.average_sales_volume-A.average_sales_volume)/(M.last_price-A.last_price) as 'price_sensitive'
                    FROM `tb_deloitte_price_sensitive_pretreatment` as A,
                    (SELECT last_price, start_date, date_add(end_date, INTERVAL 1 day) as end_date,
                    average_sales_volume, diff_days
                    FROM `tb_deloitte_price_sensitive_pretreatment`
                    WHERE prod_id='%(prod_id)s') as M
                    WHERE A.prod_id='%(prod_id)s' AND M.end_date = A.start_date''' % {'prod_id': prod_id['prod_id']}
                (line_price_sensitivity, res_price_sensitivity) = self.mysql_db_oper.exe_search(sql_price_sensitivity)
                if res_price_sensitivity:
                    for data_item in res_price_sensitivity:
                        self.load_to_db(data_item)
    def load_to_db(self, data_item):
        collecttime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(time.time())))
        sql = '''INSERT INTO tb_mk_dt_price_sensitive_dtal(prod_id, last_price, now_price, last_price_ave, 
                now_price_ave, last_price_days, now_price_days, price_sensitive, collect_time) 
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)'''
        vals = (
            data_item['prod_id'],
            data_item['last_price'],
            data_item['now_price'],
            data_item['last_price_ave'],
            data_item['now_price_ave'],
            data_item['last_price_days'],
            data_item['now_price_days'],
            data_item['price_sensitive'],
            collecttime
            )
        self.mysql_db_oper.exe_insert(sql, vals)
        print "["+collecttime+"]", u"入库成功."

a = price_sensitivity()
a.get_prod_id()