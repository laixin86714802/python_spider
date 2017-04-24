#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME:      db_helper.py
# VERSION:   1.0
# CREATED:   2016-12-22 10:04:52
# AUTHOR:    xuexiang
# DESCRIPTION:   市场价格分析类
#
# HISTORY:
#*************************************************************
from comm.mysql_helper import mysql_helper_class
import conf.db_conf
import time
import datetime

class market_price_analysis(object):
    """市场价格分析类"""
    def __init__(self):
        # MySQL20数据库对象
        self.mysql_db_oper = mysql_helper_class(conf.db_conf)
    def get_all_prod(self):
        '''获取全量商品'''
        sql_all_prod = '''SELECT comp_id, prod_id FROM `wrk_comweb_hour_price`
            WHERE prod_id is not null and prod_id != 0
            GROUP BY comp_id, prod_id'''
        (line_all_prod, res_all_prod) = self.mysql_db_oper.exe_search(sql_all_prod)
        for all_prod in res_all_prod:
            data_item = {}
            data_item['comp_id'] = all_prod['comp_id']
            data_item['prod_id'] = all_prod['prod_id']
            self.prod_price_month(data_item=data_item)

    def prod_price_month(self, data_item):
        '''获取商品当月和前三个月价格'''
        month_list = ['2015-12', '2016-01', '2016-02', '2016-03', '2016-04', '2016-05', '2016-06', '2016-07', '2016-08', '2016-09', '2016-10', '2016-11', '2016-12']
        for month in month_list:
            # 当前月份
            data_item['now_month'] = month
            # 当月均价
            data_item['now_month_ave_price'] = 0
            # 前三个月均价
            data_item['three_month_ave_price'] = 0
            # 变动比率
            data_item['change_ratio'] = 0
            # 当月价格数组
            now_month_price_list = []
            # 前三个月价格数组
            three_month_price_list = []
            now_month = month + '-01'
            now_month_date = time.strptime(now_month,'%Y-%m-%d')
            three_month = (datetime.datetime(*now_month_date[:3]) - datetime.timedelta(days=90)).strftime('%Y-%m')
            three_month = three_month + '-01'
            # 查询当前月价格
            sql_now_month_price = '''SELECT price FROM `wrk_comweb_hour_price`
                WHERE prod_id='%s' AND insert_time LIKE '%s%%'
                GROUP BY DATE_FORMAT(insert_time,'%%Y-%%m-%%d') ''' % (data_item['prod_id'], month)
            (line_now_month_price, res_now_month_price) = self.mysql_db_oper.exe_search(sql_now_month_price)
            if res_now_month_price:
                for now_month_price in res_now_month_price:
                    now_month_price_list.append(now_month_price['price'])
            else:
                # 补全并去除数组内0价格
                now_month_price_list = self.deal_with_price(price_list=now_month_price_list)
                if len(now_month_price_list) != 0:
                    data_item['now_month_ave_price'] = sum(now_month_price_list) / len(now_month_price_list)
                else:
                    data_item['now_month_ave_price'] = 0
            # 查询前三个月价格
            sql_three_month_price = '''SELECT price FROM `wrk_comweb_hour_price`
                WHERE prod_id='%s' AND insert_time BETWEEN '%s' and '%s'
                GROUP BY DATE_FORMAT(insert_time,'%%Y-%%m-%%d') ''' % (data_item['prod_id'], three_month, now_month)
            (line_three_month_price, res_three_month_price) = self.mysql_db_oper.exe_search(sql_three_month_price)
            if res_three_month_price:
                for three_month_price in res_three_month_price:
                    three_month_price_list.append(three_month_price['price'])
                # 补全并去除数组内0价格
                three_month_price_list = self.deal_with_price(price_list=three_month_price_list)
                if len(three_month_price_list) != 0:
                    data_item['three_month_ave_price'] = sum(three_month_price_list) / len(three_month_price_list)
                else:
                    data_item['three_month_ave_price'] = 0
            # 变动比率
            if data_item['three_month_ave_price'] != 0:
                data_item['change_ratio'] = (data_item['now_month_ave_price'] - data_item['three_month_ave_price']) / data_item['three_month_ave_price']
            self.load_to_db(data_item)

    def deal_with_price(self, price_list):
        '''补全并去除数组内0价格'''
        # 补全价格
        for point, price in enumerate(price_list):
            if price == 0:
                for i in range(1, 11):
                    left_point = point - i
                    right_point = point + i
                    if left_point >0 and left_point < len(price_list):
                        if price_list[left_point] != 0:
                            price_list[point] = price_list[left_point]
                            break
                    if right_point >0 and right_point < len(price_list):
                        if price_list[right_point] != 0:
                            price_list[point] = price_list[left_point]
                            break
        # 去除0元素
        price_list = [i for i in price_list if i != 0]
        return price_list

    def load_to_db(self, data_item):
        '''入库函数'''
        collecttime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(time.time())))
        sql = '''INSERT INTO tb_mk_dt_marketprice_change_mon(comp_id, prod_id, now_month, now_month_ave_price, three_month_ave_price, change_ratio, collect_time) 
                VALUES(%s, %s, %s, %s, %s, %s, %s)'''
        vals = (
            data_item['comp_id'],
            data_item['prod_id'],
            data_item['now_month'],
            data_item['now_month_ave_price'],
            data_item['three_month_ave_price'],
            data_item['change_ratio'],
            collecttime
            )
        self.mysql_db_oper.exe_insert(sql, vals)
        print "["+collecttime+"]", u"入库成功."

a = market_price_analysis()
a.get_all_prod()