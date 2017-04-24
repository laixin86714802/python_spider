#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME:      db_helper.py
# VERSION:   1.0
# CREATED:   2016-12-22 09:05:24
# AUTHOR:    xuexiang
# DESCRIPTION:   低价集中预处理类
#
# HISTORY:
#*************************************************************
from comm.mysql_helper import mysql_helper_class
import conf.db_conf
import time
import datetime

class low_price_focus_pretreatment(object):
    """低价集中预处理类"""
    def __init__(self):
        # MySQL20数据库对象
        self.mysql_db_oper = mysql_helper_class(conf.db_conf)
    def get_jk_prod_id(self):
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
        '''获取健客价格'''
        sql_jk_prod_price = '''SELECT price FROM `wrk_comweb_hour_price`
            WHERE comp_id=100000 AND prod_id='%s' AND DATE_FORMAT(insert_time,'%%Y-%%m-%%d')='%s'
            GROUP BY comp_id, prod_id ''' % (jk_prod_id, date)
        (line_jk_prod_price, res_jk_prod_price) = self.mysql_db_oper.exe_search(sql_jk_prod_price)
        if res_jk_prod_price:
            price = res_jk_prod_price[0]['price']
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

    def get_comp_mapping(self, jk_prod_id, date):
        '''获取竞争对手商品'''
        data_item = {}
        comp_price_item = []
        # 获取健客商品对应商家商品
        sql_jk_prod_mapping = '''SELECT comp_id, comp_prod_id FROM `bas_comweb_url`
            WHERE jk_prod_id='%s'
            GROUP BY jk_prod_id, comp_prod_id''' % jk_prod_id
        (line_jk_prod_mapping, res_jk_prod_mapping) = self.mysql_db_oper.exe_search(sql_jk_prod_mapping)
        for jk_prod_mapping in res_jk_prod_mapping:
            data_item['date'] = date
            data_item['comp_id'] = jk_prod_mapping['comp_id']
            data_item['comp_prod_id'] = jk_prod_mapping['comp_prod_id']
            # 提交至价格处理类
            comp_price = self.get_comp_price(data_item=data_item)
            comp_price_item.append(comp_price)
            return comp_price_item

    def get_comp_price(self, data_item):
        '''获取竞争对手价格'''
        # 获取竞争队友价格
        sql_comp_prod_price = '''SELECT price FROM `wrk_comweb_hour_price`
            WHERE comp_id='%s' AND prod_id='%s' AND DATE_FORMAT(insert_time,'%%Y-%%m-%%d')='%s' 
            GROUP BY comp_id, prod_id''' % (data_item['comp_id'], data_item['comp_prod_id'], data_item['date'])
        (line_comp_prod_price, res_comp_prod_price) = self.mysql_db_oper.exe_search(sql_comp_prod_price)
        if res_comp_prod_price:
            comp_price = res_comp_prod_price[0]['price']
            return comp_price
        else:
            # 价格异常补全
            comp_price = self.deal_with_comp_price(data_item)
            return comp_price

    def deal_with_comp_price(self, data_item):
        '''补全竞争对手价格'''
        sql_else = '''SELECT price FROM `wrk_comweb_hour_price`
            WHERE comp_id='%s' AND prod_id='%s' AND DATE_FORMAT(insert_time,'%%Y-%%m-%%d')='%s'
            GROUP BY comp_id, prod_id'''
        for day in range(1,11):
            current_date = time.strptime(data_item['date'],'%Y-%m-%d')
            left_datetime = (datetime.datetime(*current_date[:3]) - datetime.timedelta(days=day)).strftime('%Y-%m-%d')
            right_datetime = (datetime.datetime(*current_date[:3]) - datetime.timedelta(days=-day)).strftime('%Y-%m-%d')
            (line_left, res_left) = self.mysql_db_oper.exe_search(sql_else % (data_item['comp_id'], data_item["comp_prod_id"], left_datetime))
            (line_right, res_right) = self.mysql_db_oper.exe_search(sql_else % (data_item['comp_id'], data_item["comp_prod_id"], right_datetime))
            if res_left and res_left[0]['price'] != 0:
                price = res_left[0]['price']
                return price
            elif res_right and res_right[0]['price'] != 0:
                price = res_right[0]['price']
                return price
            else:
                price = 0
                return price

    def load_to_db(self,data_item):
        '''入库函数'''
        collecttime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(time.time())))
        sql = '''INSERT INTO tb_mk_dt_lowprice_focus_day_tmp(jk_id, date_time, jk_price, comp_price_min, jk_low_price, collect_time) 
                VALUES(%s, %s, %s, %s, %s, %s)'''
        vals = (
            data_item['jk_id'],
            data_item['date_time'],
            data_item['jk_price'],
            data_item['comp_price_min'],
            data_item['jk_low_price'],
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
a = low_price_focus_pretreatment()
# 获取健客总商品id
jk_prod_id_item = a.get_jk_prod_id()
data_item = {}
date_item = a.datelist((2016, 01, 05), (2016, 12, 25))

for date in date_item:
    for jk_prod_id in jk_prod_id_item:
        data_item['jk_id'] = int(jk_prod_id)
        data_item['date_time'] = date
        data_item['jk_price'] = a.get_jk_price(jk_prod_id=jk_prod_id, date=date)
        comp_price = a.get_comp_mapping(jk_prod_id=jk_prod_id, date=date)
        data_item['comp_price_min'] = min(comp_price)
        if data_item['jk_price'] and data_item['comp_price_min']:
            if data_item['jk_price'] <= data_item['comp_price_min']:
                data_item['jk_low_price'] = 1
            else:
                data_item['jk_low_price'] = 0
            a.load_to_db(data_item)