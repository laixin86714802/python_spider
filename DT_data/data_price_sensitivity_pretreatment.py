#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME:      db_helper.py
# VERSION:   1.0
# CREATED:   2016-12-21 16:51:07
# AUTHOR:    xuexiang
# DESCRIPTION:   数据入库类
#
# HISTORY:
#*************************************************************
from comm.sqlser_helper import sqlser_helper_class
from comm.mysql_helper import mysql_helper_class
import conf.db_conf
import datetime
import time

class price_sensitivity_pretreatment(object):
    """指标五：价格敏感度数据预处理"""
    def __init__(self):
        # SQLServer17数据库对象
        self.sqlser_db_oper = sqlser_helper_class(conf.db_conf)
        # MySQL20数据库对象
        self.mysql_db_oper = mysql_helper_class(conf.db_conf)
    def price_change(self):
        '''获取价格变化并补全数据'''
        sql_jk_prod = '''SELECT jk_prod_id FROM `bas_comweb_url` GROUP BY jk_prod_id '''
        (line_jk_prod, res_jk_prod) = self.mysql_db_oper.exe_search(sql_jk_prod)
        data_item = {}
        for jk_prod in res_jk_prod:
            data_item['prod_id'] = jk_prod['jk_prod_id']
            sql_price_arr = '''SELECT price, date_format(insert_time, '%%Y-%%m-%%d') as 'date' 
                FROM `wrk_comweb_hour_price`
                WHERE prod_id='%s'
                GROUP BY date_format(insert_time, '%%Y-%%m-%%d')''' % data_item['prod_id']
            (line_price_arr, res_price_arr) = self.mysql_db_oper.exe_search(sql_price_arr)
            if res_price_arr:
                price_arr = []
                date_arr = []
                # 获取价格数据
                for price_item in res_price_arr:
                    price_arr.append(price_item['price'])
                    date_arr.append(price_item['date'])
                # 补全数据
                for point, price_value in enumerate(price_arr):
                    if price_value == 0:
                        for i in range(1, 11):
                            left_point = point - i
                            right_point = point + i
                            if left_point >0 and left_point < len(price_arr):
                                if price_arr[left_point] != 0:
                                    price_arr[point] = price_arr[left_point]
                                    break
                            if right_point >0 and right_point < len(price_arr):
                                if price_arr[right_point] != 0:
                                    price_arr[point] = price_arr[left_point]
                                    break
                # 当前价格起始日期
                data_item['start_date'] = date_arr[0]
                # 当前价格终止日期
                data_item['end_date'] = ""
                # 上一价格
                data_item['last_price'] = price_arr[0]
                # 当前价格
                data_item['now_price'] = None
                # 当前价格天数
                data_item['diff_days'] = 0
                # 获取当前价格的始末日期信息
                for point, price_value in enumerate(price_arr):
                    if point + 1 < len(price_arr):
                        if price_arr[point+1] != price_arr[point]:
                            data_item['now_price'] = price_arr[point+1]
                            data_item['end_date'] = date_arr[point]
                            start_date_time = time.strptime(data_item['start_date'],'%Y-%m-%d')
                            end_date_time = time.strptime(data_item['end_date'],'%Y-%m-%d')
                            # 计算始末日期相差天数
                            start_date = datetime.datetime(start_date_time[0],start_date_time[1],start_date_time[2])
                            end_date = datetime.datetime(end_date_time[0],end_date_time[1],end_date_time[2])
                            data_item['diff_days'] = (end_date - start_date).days + 1
                            self.sales_volume(data_item)
                            # 重置起始日期和价格
                            data_item['start_date'] = (datetime.datetime(*end_date_time[:3]) - datetime.timedelta(days=-1)).strftime('%Y-%m-%d')
                            data_item['last_price'] = data_item['now_price']
                    else:
                        data_item['end_date'] = date_arr[point]
                        # 计算始末日期相差天数
                        start_date_time = time.strptime(data_item['start_date'],'%Y-%m-%d')
                        end_date_time = time.strptime(data_item['end_date'],'%Y-%m-%d')
                        # 计算始末日期相差天数
                        start_date = datetime.datetime(start_date_time[0],start_date_time[1],start_date_time[2])
                        end_date = datetime.datetime(end_date_time[0],end_date_time[1],end_date_time[2])
                        data_item['diff_days'] = (end_date - start_date).days + 1
                        self.sales_volume(data_item)


    def sales_volume(self, data_item):
        '''当前价格销量'''
        if data_item['now_price'] == None:
            data_item['now_price'] = data_item['last_price']
        # 当前价格销量
        data_item['sales_volume'] = 0
        # 日均销量
        data_item['average_sales_volume'] = 0
        end_date = time.strptime(data_item['end_date'],'%Y-%m-%d')
        right_datetime = (datetime.datetime(*end_date[:3]) - datetime.timedelta(days=-1)).strftime('%Y-%m-%d')
        sql_sales_volume = '''SELECT M.Amount
            FROM TB_Inf_Map_Orders as A,
            (SELECT ProductCode, OrdersCode, Amount
            FROM TB_Inf_Map_OrderProducts
            WHERE CreationDate BETWEEN '%(start_time)s' AND '%(end_time)s' AND ProductCode='%(id)s') as M
            WHERE A.OrdersCode = M.OrdersCode AND A.OrderStatus NOT IN (80, 180, 200)''' % {'start_time': data_item['start_date'], 'end_time': right_datetime, 'id': data_item['prod_id']}
        sales_volume = self.sqlser_db_oper.ExecQuery(sql_sales_volume)
        if sales_volume:
            for sale_item in sales_volume:
                data_item['sales_volume'] = data_item['sales_volume'] + sale_item[0]
            data_item['average_sales_volume'] = float(data_item['sales_volume']) / float(data_item['diff_days'])
        self.load_to_db(data_item)
    def load_to_db(self, data_item):
        '''入库函数'''
        collecttime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(time.time())))
        sql = '''INSERT INTO tb_mk_dt_price_sensitive_dtal_tmp(prod_id, last_price, now_price, start_date, end_date, diff_days, sales_volume, average_sales_volume, collect_time) 
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)'''
        vals = (
            data_item['prod_id'],
            data_item['last_price'],
            data_item['now_price'],
            data_item['start_date'],
            data_item['end_date'],
            data_item['diff_days'],
            data_item['sales_volume'],
            data_item['average_sales_volume'],
            collecttime
            )
        self.mysql_db_oper.exe_insert(sql, vals)
        print "["+collecttime+"]", u"入库成功."

a = price_sensitivity_pretreatment()
a.price_change()