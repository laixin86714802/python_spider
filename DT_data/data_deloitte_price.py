#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME:      db_helper.py
# VERSION:   1.0
# CREATED:   2016-12-14 12:50
# AUTHOR:    xuexiang
# DESCRIPTION:   德勤需求销售数据相关类
#
# HISTORY:
#*************************************************************
from comm.sqlser_helper import sqlser_helper_class
from comm.mysql_helper import mysql_helper_class
import conf.db_conf
import time
import datetime

class Sales_volume(object):
    """指标一~四：销售数据相关"""
    def __init__(self):
        # SQLServer17数据库对象
        self.sqlser_db_oper = sqlser_helper_class(conf.db_conf)
        # MySQL20数据库对象
        self.mysql_db_oper = mysql_helper_class(conf.db_conf)

    def get_jk_prod(self):
        '''获取健客商品'''
        jk_prod_id = []
        # 获取健客商品
        sql_jk_prod = '''SELECT jk_prod_id FROM `bas_comweb_url`
                GROUP BY jk_prod_id'''
        (line_jk_prod, res_jk_prod) = self.mysql_db_oper.exe_search(sql_jk_prod)
        for jk_prod in res_jk_prod:
            jk_prod_id.append(jk_prod['jk_prod_id'])
        return jk_prod_id

    def get_jk_price(self, jk_prod_id, date):
        '''获取健客当天价格'''
        # 获取当天数据
        sql = '''SELECT price FROM `wrk_comweb_hour_price`
            WHERE comp_id=100000 AND prod_id='%s' AND DATE_FORMAT(insert_time,'%%Y-%%m-%%d')='%s'
            GROUP BY comp_id, prod_id ''' % (jk_prod_id, date)
        (line_cnt, res_cnt) = self.mysql_db_oper.exe_search(sql)
        if res_cnt:
            price = res_cnt[0]['price']
            return price
        else:
            # 价格异常补全
            price = self.deal_with_jk_price(jk_prod_id=jk_prod_id, date=date)
            return price

    def deal_with_jk_price(self, jk_prod_id, date):
        '''补全健客价格'''
        sql_else = '''SELECT price FROM `wrk_comweb_hour_price`
            WHERE comp_id=100000 AND prod_id='%s' AND DATE_FORMAT(insert_time,'%%Y-%%m-%%d')='%s'
            GROUP BY comp_id, prod_id'''
        for day in range(1,11):
            current_date = time.strptime(date,'%Y-%m-%d')
            left_datetime = (datetime.datetime(*current_date[:3]) - datetime.timedelta(days=day)).strftime('%Y-%m-%d')
            right_datetime = (datetime.datetime(*current_date[:3]) - datetime.timedelta(days=-day)).strftime('%Y-%m-%d')
            (line_left, res_left) = self.mysql_db_oper.exe_search(sql_else % (jk_prod_id, left_datetime))
            (line_right, res_right) = self.mysql_db_oper.exe_search(sql_else % (jk_prod_id, right_datetime))
            if res_left and res_left[0]['price'] != 0:
                price = res_left[0]['price']
                return price
            elif res_right and res_right[0]['price'] != 0:
                price = res_right[0]['price']
                return price
            else:
                price = 0
                return price

    def get_priceself_sale_num(self, data_item):
        '''计算当天该商品的销量和销售额'''
        sql_sale_num = '''SELECT sum(M.Amount) as sale_num, sum(M.Amount*M.ActualPrice/100.0) as sales_volume
            FROM TB_Inf_Map_Orders as A,
            (SELECT OrdersCode, Amount, ActualPrice FROM TB_Inf_Map_OrderProducts WHERE CONVERT(varchar(10), CreationDate, 120) = '%s' and ProductCode = '%s') as M
            WHERE A.OrdersCode = M.OrdersCode AND A.OrderStatus not in (80, 180, 200)
        ''' % (data_item['date'], data_item['prod_id'])
        sale_num = self.sqlser_db_oper.ExecQuery(sql_sale_num)
        # 销量
        data_item['sale_num'] = 0
        # 销售额
        data_item['sales_volume'] = 0
        if sale_num[0]:
            if sale_num[0][0]:
                data_item['sale_num'] = sale_num[0][0]
            if sale_num[0][1]:
                data_item['sales_volume'] = sale_num[0][1]
        else:
            data_item['sale_num'] = 0
            data_item['sales_volume'] = 0
        print u"已获取销量、销售额"
        self.get_purchase_price(data_item)

    def get_purchase_price(self, data_item):
        '''获取采购价'''
        sql_purchase_price = "SELECT PurchasePrice FROM TB_Inf_Map_Product where ProductCode = '%s'" % data_item["prod_id"]
        purchase_price = self.sqlser_db_oper.ExecQuery(sql_purchase_price)
        # 采购价
        data_item['purchase_price'] = 0
        # 毛利率
        data_item['gross_margin'] = 0
        # 毛利
        data_item['gross_profit'] = 0
        if purchase_price:
            data_item['purchase_price'] = int(purchase_price[0][0]) / 100.0
            if data_item['purchase_price'] != 0:
                data_item['gross_margin'] = (int(data_item['price']) - data_item['purchase_price']) / data_item['purchase_price']
                data_item['gross_profit'] = data_item['gross_margin'] * float(data_item['sales_volume'])
        print u"已获取采购价、毛利率"
        self.get_low_price(data_item)

    def get_low_price(self, data_item):
        '''获取市场次低价'''
        sql_comp_prod_id = '''SELECT comp_prod_id FROM `bas_comweb_url` WHERE jk_prod_id='%s' '''
        (line_comp_prod_id, res_comp_prod_id) = self.mysql_db_oper.exe_search(sql_comp_prod_id % data_item['prod_id'])
        # 获取健客商品和对应竞争对手商品数组
        prod_id = []
        if res_comp_prod_id:
            for comp_prod_id in res_comp_prod_id:
                prod_id.append(comp_prod_id['comp_prod_id'])
        prod_id.append(data_item['prod_id'])
        prod_id = [str(i) for i in prod_id]
        sql = '''SELECT prod_id, price
            FROM wrk_comweb_hour_price
            WHERE prod_id in (%s) AND insert_time LIKE '%s%%'
            GROUP BY prod_id''' % (','.join(prod_id), data_item['date'])

        (line_low_price, res_low_price) = self.mysql_db_oper.exe_search(sql)
        # 次低价
        data_item['low_price'] = 0
        # 定价差
        data_item['price_diff'] = 0
        # 差价比
        data_item['price_diff_ratio'] = 0
        if res_low_price:
            price_arr = []
            # 遍历该商品当天不同价格
            for price_item in res_low_price:
                price_arr.append(price_item['price'])
            # 价格数组去重, 排序, 取次低价
            if price_arr:
                # 去零
                price_arr = [i for i in price_arr if i != 0]
                # 去重
                price_arr = list(set(price_arr))
                print u"已获取次低价"
                if len(price_arr) >= 2:
                    # 排序
                    price_arr.sort()
                    data_item['low_price'] = price_arr[1]
                    data_item['price_diff'] = float(data_item['price']) - float(data_item['low_price'])
                    if data_item['low_price'] != 0:
                        data_item['price_diff_ratio'] = data_item['price_diff'] / float(data_item['low_price'])
                elif len(price_arr) == 1:
                    data_item['low_price'] = price_arr[0]
                    data_item['price_diff'] = float(data_item['price']) - float(data_item['low_price'])
                    if data_item['low_price'] != 0:
                        data_item['price_diff_ratio'] = data_item['price_diff'] / float(data_item['low_price'])
            else:
                data_item['low_price'] = 0
        print u"准备入库"
        self.load_to_db(data_item)

    def load_to_db(self, data_item):
        '''入库函数'''
        collecttime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(time.time())))
        sql = '''INSERT INTO tb_mk_dt_price_data_day(prod_code, price, sale_num, sales_volume, purchase_price, gross_margin, gross_profit, low_price, price_diff, price_diff_ratio, date_time, collect_time) 
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
        vals = (
            data_item['prod_id'],
            data_item['price'],
            data_item['sale_num'],
            data_item['sales_volume'],
            data_item['purchase_price'],
            data_item['gross_margin'],
            data_item['gross_profit'],
            data_item['low_price'],
            data_item['price_diff'],
            data_item['price_diff_ratio'],
            data_item['date'],
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

a = Sales_volume()
data_item = {}
jk_prod_id_item = a.get_jk_prod()
date_item = a.datelist((2016, 01, 26), (2017, 01, 03))
for date in date_item:
    for jk_prod_id in jk_prod_id_item:
        data_item['prod_id'] = int(jk_prod_id)
        data_item['date'] = date
        data_item['price'] = a.get_jk_price(jk_prod_id=jk_prod_id, date=date)
        a.get_priceself_sale_num(data_item)