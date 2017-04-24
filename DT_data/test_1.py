#!/usr/bin/python
# coding:utf-8
import datetime
import time
from comm.mysql_helper import mysql_helper_class
import conf.db_conf
from comm.sqlser_helper import sqlser_helper_class

def datelist(start, end):
    '''日期列表'''
    start_date = datetime.date(*start)
    end_date = datetime.date(*end)
    result = []
    curr_date = start_date
    while curr_date != end_date:
        result.append("%04d-%02d-%02d" % (curr_date.year, curr_date.month, curr_date.day))
        curr_date += datetime.timedelta(1)
    result.append("%04d-%02d-%02d" % (curr_date.year, curr_date.month, curr_date.day))
    return result

def get_jk_price(jk_prod_id, date):
    '''获取健客价格'''
    mysql_db_oper = mysql_helper_class(conf.db_conf)
    sql_jk_prod_price = '''SELECT price FROM `wrk_comweb_hour_price`
        WHERE comp_id=100000 AND prod_id='%s' AND DATE_FORMAT(insert_time,'%%Y-%%m-%%d')='%s'
        GROUP BY comp_id, prod_id ''' % (jk_prod_id, date)
    (line_jk_prod_price, res_jk_prod_price) = mysql_db_oper.exe_search(sql_jk_prod_price)
    
    if res_jk_prod_price:
        price = res_jk_prod_price[0]['price']
        return price
    else:
        # 价格异常补全
        price = deal_with_jk_price(jk_prod_id=jk_prod_id, date=date)
        return price

def deal_with_jk_price(jk_prod_id, date):
    '''补全健客价格'''
    mysql_db_oper = mysql_helper_class(conf.db_conf)
    sql_else = '''SELECT price FROM `wrk_comweb_hour_price`
        WHERE comp_id=100000 AND prod_id='%s' AND DATE_FORMAT(insert_time,'%%Y-%%m-%%d')='%s'
        GROUP BY comp_id, prod_id'''
    for day in range(1,11):
        current_date = time.strptime(date,'%Y-%m-%d')
        left_datetime = (datetime.datetime(*current_date[:3]) - datetime.timedelta(days=day)).strftime('%Y-%m-%d')
        right_datetime = (datetime.datetime(*current_date[:3]) - datetime.timedelta(days=-day)).strftime('%Y-%m-%d')
        (line_left, res_left) = mysql_db_oper.exe_search(sql_else % (jk_prod_id, left_datetime))
        (line_right, res_right) = mysql_db_oper.exe_search(sql_else % (jk_prod_id, right_datetime))
        if res_left and res_left[0]['price'] != 0:
            price = res_left[0]['price']
            return price
        elif res_right and res_right[0]['price'] != 0:
            price = res_right[0]['price']
            return price
        else:
            price = 0
            return price

date_item = datelist((2015, 12, 25), (2016, 12, 31))
mysql_db_oper = mysql_helper_class(conf.db_conf)
sqlser_db_oper = sqlser_helper_class(conf.db_conf)

current_date = time.strptime('2015-12-25','%Y-%m-%d')
date=[322,323,324,325,326]
for i in date:
    right_datetime = (datetime.datetime(*current_date[:3]) + datetime.timedelta(days=(i-1))).strftime('%Y-%m-%d')
    print right_datetime