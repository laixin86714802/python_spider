#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME:      db_helper.py
# VERSION:   1.0
# CREATED:   2016-12-27 15:13:47
# AUTHOR:    xuexiang
# DESCRIPTION:   低价销量类
#
# HISTORY:
#*************************************************************
from comm.sqlser_helper import sqlser_helper_class
from comm.mysql_helper import mysql_helper_class
import conf.db_conf
import time

class low_price_sales(object):
    """低价销量类"""
    def __init__(self):
        # SQLServer17数据库对象
        self.sqlser_db_oper = sqlser_helper_class(conf.db_conf)
        # MySQL20数据库对象
        self.mysql_db_oper = mysql_helper_class(conf.db_conf)

    def get_low_price_prod(self, date_time):
        '''获取当月健客最低价商品'''
        data_item = {}
        sales_volume_arr = []
        sql_low_price_prod = ''' SELECT jk_id FROM `tb_deloitte_low_price_num_pretreatment`
            WHERE date_time='%s' and jk_low_price = 1 ''' % date_time
        (line_low_price_prod, res_low_price_prod) = self.mysql_db_oper.exe_search(sql_low_price_prod)
        for low_price_prod in res_low_price_prod:
            data_item['date_time'] = date_time
            data_item['jk_id'] = low_price_prod['jk_id']
            # 提交至获取低价商品销售额
            sales_volume = self.get_low_price_sales(data_item)
            # 添加至本月低价商品销售额数组中
            sales_volume_arr.append(sales_volume)
        # 获取本月低价商品销售额
        data_item['sales_volume'] = sum(sales_volume_arr)
        # 获取本月监控商品总销售额
        data_item['all_sales_volume'] = self.get_all_sales_volume(data_item)
        # 获取低价销量比例
        data_item['low_price_ratio'] = (data_item['sales_volume']/data_item['all_sales_volume'])
        # 入库
        self.load_to_db(data_item)

    def get_low_price_sales(self, data_item):
        '''获取低价商品销售额'''
        sales_volume = 0
        sql_low_price_sales = '''SELECT sales_volume FROM `tb_mk_dt_price_data_day`
            WHERE prod_code = '%s' AND date_time like '%s%%' ''' % (data_item['jk_id'], data_item['date_time'])
        (line_low_price_sales, res_low_price_sales) = self.mysql_db_oper.exe_search(sql_low_price_sales)
        if res_low_price_sales:
            for low_price_sales in res_low_price_sales:
                sales_volume += low_price_sales['sales_volume']
        return sales_volume

    def get_all_sales_volume(self, data_item):
        '''获取本月总销售额'''
        all_sales_volume = 0
        sql_all_sales_volume = '''SELECT SUM(sales_volume) as 'all_sales_volume' FROM `tb_mk_dt_price_data_day`
            WHERE date_time like '%s%%' ''' % data_item['date_time']
        (line_all_sales_volume, res_all_sales_volume) = self.mysql_db_oper.exe_search(sql_all_sales_volume)
        if res_all_sales_volume:
            all_sales_volume = res_all_sales_volume[0]['all_sales_volume']
        return all_sales_volume

    def load_to_db(self, data_item):
        '''入库函数'''
        collecttime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(time.time())))
        sql='''INSERT INTO tb_shw_dt_lowprice_sales_mon(date_time, sales_volume, all_sales_volume, low_price_ratio, collect_time) 
                VALUES(%s, %s, %s, %s, %s)'''
        vals = (
            data_item['date_time'],
            data_item['sales_volume'],
            data_item['all_sales_volume'],
            data_item['low_price_ratio'],
            collecttime
            )
        self.mysql_db_oper.exe_insert(sql, vals)
        print "["+collecttime+"]", u"入库成功."
'''主函数'''
month_list = ['2015-12', '2016-01', '2016-02', '2016-03', '2016-04', '2016-05', '2016-06', '2016-07', '2016-08', '2016-09', '2016-10', '2016-11', '2016-12']
a = low_price_sales()
for month in month_list:
    a.get_low_price_prod(date_time=month)