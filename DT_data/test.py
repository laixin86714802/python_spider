#!/usr/bin/python
# coding:utf-8
# from comm.mysql_helper import mysql_helper_class
# import conf.db_conf
import datetime
import test_0
def datelist(start, end):
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
date_item = datelist((2015, 12, 25), (2017, 01, 03))
item = {}
date_arr = test_0.date_arr
count = test_0.count
for date in date_item:
    if date in date_arr:
        item[date] = count[date_arr.index(date)]
    else:
        item[date] = 0
    # open('a.txt', 'a+').write(date+'\n')
    open('b.txt', 'a+').write(str(item[date])+',\n')