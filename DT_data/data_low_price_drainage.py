#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME:      db_helper.py
# VERSION:   1.0
# CREATED:   2016-12-27 20:11:48
# AUTHOR:    xuexiang
# DESCRIPTION:   低价引流类
#
# HISTORY:
#*************************************************************
from comm.sqlser_helper import sqlser_helper_class
from comm.mysql_helper import mysql_helper_class
import conf.db_conf
import time
import datetime

class low_price_drainage(object):
    """低价引流类"""
    def __init__(self):
        # SQLServer17数据库对象
        self.sqlser_db_oper = sqlser_helper_class(conf.db_conf)
        # MySQL20数据库对象
        self.mysql_db_oper = mysql_helper_class(conf.db_conf)
        # 读取偏移值
        self.offset_num = 0

    def get_low_price_inf(self, date_time):
        '''获取该日期低价商品id'''
        data_item = {}
        # 当天低价商品id列表
        prod_id = []
        sql_low_price_inf = '''SELECT jk_id, date_time FROM `tb_mk_dt_lowprice_focus_day_tmp`
            WHERE date_time = '%s' ''' % date_time
        (line_low_price_inf, res_low_price_inf) = self.mysql_db_oper.exe_search(sql_low_price_inf)
        if res_low_price_inf:
            for low_price_inf in res_low_price_inf:
                prod_id.append(low_price_inf['jk_id'])
                data_item['date_time'] = low_price_inf['date_time']
            self.get_low_price_ordercode(data_item=data_item, prod_id=prod_id)

    def get_low_price_ordercode(self, data_item, prod_id):
        '''获取当日存在低价商品的订单号'''
        prod_id_str = [str(i) for i in prod_id]
        sql_low_price_order = '''SELECT M.OrdersCode
            FROM TB_Inf_Map_Orders as A, 
            (SELECT OrdersCode
            FROM TB_Inf_Map_OrderProducts
            WHERE ProductCode IN (%s) AND CONVERT(varchar(10), CreationDate, 120)='%s') as M
            WHERE M.OrdersCode = A.OrdersCode 
            AND A.OrderStatus NOT IN (80, 180, 200)
            GROUP BY M.OrdersCode''' % (','.join(prod_id_str), data_item['date_time'])
        low_price_order = self.sqlser_db_oper.ExecQuery(sql_low_price_order)
        if low_price_order:
            for order in low_price_order:
                data_item['order_code'] = order[0]
                self.get_low_price_prod(data_item, prod_id=prod_id)

    def get_low_price_prod(self, data_item, prod_id):
        '''获取低价订单中商品'''
        # 低价产品销售额
        data_item['low_price_sales'] = 0
        # 订单总销售额
        data_item['all_sales'] = 0
        sql_low_price_prod = '''SELECT OrdersCode, ProductCode, Amount, 
            CASE WHEN OurPrice = 0 THEN ActualPrice/100.0
            ELSE OurPrice/100.0
            END as OurPrice
            FROM TB_Inf_Map_OrderProducts
            WHERE OrdersCode = '%s'  AND ProductCode != 307261''' % (data_item['order_code'])
        low_price_prod = self.sqlser_db_oper.ExecQuery(sql_low_price_prod)
        if low_price_prod:
            for prod in low_price_prod:
                if prod[1] in prod_id:
                    data_item['low_price_sales'] += prod[2]*prod[3]
                data_item['all_sales'] += prod[2]*prod[3]
                if data_item['all_sales']:
                    data_item['drainage'] = data_item['low_price_sales']/data_item['all_sales']
                else:
                    data_item['drainage'] = 0
            self.load_to_db(data_item)

    def load_to_db(self, data_item):
        '''入库函数'''
        collecttime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(time.time())))
        sql = '''INSERT INTO tb_mk_dt_lowprice_drainage_day(date_time, order_code, drainage, low_price_sales, all_sales, collect_time) 
                VALUES(%s, %s, %s, %s, %s, %s)'''
        vals = (
            data_item['date_time'],
            data_item['order_code'],
            data_item['drainage'],
            data_item['low_price_sales'],
            data_item['all_sales'],
            collecttime
            )
        self.mysql_db_oper.exe_insert(sql, vals)
        print "["+collecttime+"]", u"入库成功."

    def datelist(self, start, end):
        '''生成日期列表'''
        start_date = datetime.date(*start)
        end_date = datetime.date(*end)
        result = []
        curr_date = start_date
        while curr_date != end_date:
            result.append("%04d-%02d-%02d" % (curr_date.year, curr_date.month, curr_date.day))
            curr_date += datetime.timedelta(1)
        result.append("%04d-%02d-%02d" % (curr_date.year, curr_date.month, curr_date.day))
        return result

'''主函数'''
a = low_price_drainage()
date = a.datelist((2016, 11, 13), (2016, 12, 29))
for i in date:
    a.get_low_price_inf(i)