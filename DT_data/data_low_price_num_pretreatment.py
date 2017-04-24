#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME:      db_helper.py
# VERSION:   1.0
# CREATED:   2016-12-27 10:06:20
# AUTHOR:    xuexiang
# DESCRIPTION:   低价数量比例预处理类
#
# HISTORY:
#*************************************************************
from comm.mysql_helper import mysql_helper_class
import conf.db_conf
import time

class low_price_num(object):
    """低价数量比例类"""
    def __init__(self):
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
        '''获取当月健客该商品均价'''
        jk_prod_price_arr = []
        sql_jk_prod_price = '''SELECT price FROM `wrk_comweb_hour_price`
            WHERE comp_id=100000 AND prod_id='%s' AND insert_time LIKE '%s%%'
            GROUP BY DATE_FORMAT(insert_time,'%%Y-%%m-%%d') ''' % (jk_prod_id, date)
        (line_jk_prod_price, res_jk_prod_price) = self.mysql_db_oper.exe_search(sql_jk_prod_price)
        if res_jk_prod_price:
            for jk_prod_price in res_jk_prod_price:
                jk_prod_price_arr.append(jk_prod_price['price'])
            # 价格异常补全
            jk_prod_price_arr = self.deal_with_price(price_list=jk_prod_price_arr)
            if jk_prod_price_arr:
                jk_prod_ave_price = sum(jk_prod_price_arr) / len(jk_prod_price_arr)
                return jk_prod_ave_price
            else:
                return 0

    def get_comp_mapping(self, jk_prod_id, date):
        '''获取竞争对手商品, 返回当月均价数组'''
        data_item = {}
        comp_price_item = []
        # 获取健客商品对应竞争商家商品
        sql_jk_prod_mapping = '''SELECT comp_id, comp_prod_id FROM `bas_comweb_url`
            WHERE jk_prod_id = '%s'
            GROUP BY jk_prod_id, comp_prod_id''' % jk_prod_id
        (line_jk_prod_mapping, res_jk_prod_mapping) = self.mysql_db_oper.exe_search(sql_jk_prod_mapping)
        for jk_prod_mapping in res_jk_prod_mapping:
            data_item['comp_id'] = jk_prod_mapping['comp_id']
            data_item['comp_prod_id'] = jk_prod_mapping['comp_prod_id']
            # 提交至价格处理类
            comp_price = self.get_comp_price(data_item=data_item, date=date)
            comp_price_item.append(comp_price)
        return comp_price_item

    def get_comp_price(self, data_item, date):
        '''获取竞争对手当月该商品均价'''
        comp_prod_price_arr = []
        sql_comp_prod_price = '''SELECT price FROM `wrk_comweb_hour_price`
            WHERE comp_id='%s' AND prod_id='%s' AND insert_time LIKE '%s%%'
            GROUP BY DATE_FORMAT(insert_time,'%%Y-%%m-%%d') ''' % (data_item['comp_id'], data_item['comp_prod_id'], date)
        (line_comp_prod_price, res_comp_prod_price) = self.mysql_db_oper.exe_search(sql_comp_prod_price)
        if res_comp_prod_price:
            for comp_prod_price in res_comp_prod_price:
                comp_prod_price_arr.append(comp_prod_price['price'])
            # 价格异常补全
            comp_prod_price_arr = self.deal_with_price(price_list=comp_prod_price_arr)
            if comp_prod_price_arr:
                comp_prod_ave_price = sum(comp_prod_price_arr) / len(comp_prod_price_arr)
                return comp_prod_ave_price
            else:
                return 0

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
        sql = '''INSERT INTO tb_mk_dt_lowprice_num_mon_tmp(jk_id, jk_ave_price, comp_low_price, jk_low_price, date_time, collect_time) 
                VALUES(%s, %s, %s, %s, %s, %s)'''
        vals = (
            data_item['jk_id'],
            data_item['jk_ave_price'],
            data_item['comp_low_price'],
            data_item['jk_low_price'],
            data_item['date_time'],
            collecttime
            )
        self.mysql_db_oper.exe_insert(sql, vals)
        print "["+collecttime+"]", u"入库成功."

'''主函数'''
month_list = ['2015-12', '2016-01', '2016-02', '2016-03', '2016-04', '2016-05', '2016-06', '2016-07', '2016-08', '2016-09', '2016-10', '2016-11', '2016-12']
a = low_price_num()
jk_prod_arr = a.get_jk_prod()
data_item = {}
for month in month_list:
    for jk_prod in jk_prod_arr:
        jk_prod_ave_price = a.get_jk_price(jk_prod_id=jk_prod, date=month)
        comp_prod_ave_price_arr = a.get_comp_mapping(jk_prod_id=jk_prod, date=month)
        # 去除空元素
        comp_prod_ave_price_arr = [i for i in comp_prod_ave_price_arr if i != 0 and i]
        if jk_prod_ave_price and comp_prod_ave_price_arr:
            if jk_prod_ave_price <= min(comp_prod_ave_price_arr):
                data_item['jk_low_price'] =  1
            else:
                data_item['jk_low_price'] =  0
            data_item['jk_id'] = jk_prod
            data_item['jk_ave_price'] = jk_prod_ave_price
            data_item['comp_low_price'] = min(comp_prod_ave_price_arr)
            data_item['date_time'] = month
            a.load_to_db(data_item)