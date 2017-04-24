#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 tmall_health_prods_list_main.py
# VERSION: 	 1.0
# CREATED: 	 2016-05-18 16:32
# AUTHOR: 	 xuexiang
# DESCRIPTION:
#
# HISTORY:
#*************************************************************
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from tmall_health_prods_list_class import tmall_health_prods_list_class

if __name__ == '__main__':

    app = tmall_health_prods_list_class()

    #设置开始状态 
    app.set_start()

    # 01-伊美食品专营店
    app.do_main(
        'https://bjymsp.tmall.com/category.htm?search=y&orderType=hotsell_desc&pageNo=1',
        '67731212',
        '01-伊美食品专营店')

    # 02-欣希安保健品专营店
    app.do_main(
        'https://xxabjp.tmall.com/category.htm?search=y&orderType=hotsell_desc&pageNo=1',
        '108543329',
        '02-欣希安保健品专营店')

    # 03-欧德凯保健专营店
    app.do_main(
        'https://oudekai.tmall.com/category.htm?search=y&orderType=hotsell_desc&pageNo=1',
        '57302028',
        '03-欧德凯保健专营店')

    # 04-善美堂保健品专营店
    app.do_main(
        'https://smtbjp.tmall.com/category.htm?search=y&orderType=hotsell_desc&pageNo=1',
        '116743176',
        '04-善美堂保健品专营店')

    # 05-格林莱保健品专营店
    app.do_main(
        'https://gllbjp.tmall.com/category.htm?search=y&orderType=hotsell_desc&pageNo=1',
        '103917884',
        '05-格林莱保健品专营店')

    # 06-萌傲保健品专营店
    app.do_main(
        'https://mengaobjp.tmall.com/category.htm?search=y&orderType=hotsell_desc&pageNo=1',
        '113596263',
        '06-萌傲保健品专营店')

    # 07-弘旺保健品专营店
    app.do_main(
        'https://hongwangbjp.tmall.com/category.htm?search=y&orderType=hotsell_desc&pageNo=1',
        '120228528',
        '07-弘旺保健品专营店')

    # 08-碧源清旗舰店
    app.do_main(
        'https://biyuanqing.tmall.com/category.htm?search=y&orderType=hotsell_desc&pageNo=1',
        '113730509',
        '08-碧源清旗舰店')

    # 09-可瑞特食品专营店
    app.do_main(
        'https://krtsp.tmall.com/category.htm?search=y&orderType=hotsell_desc&pageNo=1',
        '72939681',
        '09-可瑞特食品专营店')

    # 10-雅培保健品旗舰店
    app.do_main(
        'https://yapeibjp.tmall.com/category.htm?search=y&orderType=hotsell_desc&pageNo=1',
        '113493946',
        '10-雅培保健品旗舰店')

    # 11-新稀宝保健食品专营
    app.do_main(
        'https://xxbbjsp.tmall.com/category.htm?search=y&orderType=hotsell_desc&pageNo=1',
        '60190410',
        '11-新稀宝保健食品专营')

    # 12-潮氏食品专营店
    app.do_main(
        'https://cssp.tmall.com/category.htm?search=y&orderType=hotsell_desc&pageNo=1',
        '60532849',
        '12-潮氏食品专营店')

    # 13-康佰保健品专营店
    app.do_main(
        'https://kbbjp.tmall.com/category.htm?search=y&orderType=hotsell_desc&pageNo=1',
        '57576614',
        '13-康佰保健品专营店')

    # 14-星隆保健食品专营店
    app.do_main(
        'https://xlbjsp.tmall.com/category.htm?search=y&orderType=hotsell_desc&pageNo=1',
        '64779864',
        '14-星隆保健食品专营店')

    # 15-顶生保健食品专营店
    app.do_main(
        'https://dsbjsp.tmall.com/category.htm?search=y&orderType=hotsell_desc&pageNo=1',
        '67979236',
        '15-顶生保健食品专营店')

    # l6-顶生保健食品专营店
    app.do_main(
        'https://xzqbjp.tmall.com/category.htm?search=y&orderType=hotsell_desc&pageNo=1',
        '103962792',
        '16-祥之情保健品专营店')

    # l7-顶生保健食品专营店
    app.do_main(
        'https://lebbjp.tmall.com/category.htm?search=y&orderType=hotsell_desc&pageNo=1',
        '108877395',
        '17-六二八保健品专营店')

    # l8-顶生保健食品专营店
    app.do_main(
        'https://bblsbjp.tmall.com/category.htm?search=y&orderType=hotsell_desc&pageNo=1',
        '105244429',
        '18-芭芭伦萨保健品专营店')

    # l9-传承堂食品专营店
    app.do_main(
        'https://cctsp.tmall.com/category.htm?search=y&orderType=hotsell_desc&pageNo=1',
        '66093502',
        '19-传承堂食品专营店')

    # 20-瑞兰康保健品专营店
    app.do_main(
        'https://rlkbjp.tmall.com/category.htm?search=y&orderType=hotsell_desc&pageNo=1',
        '106002289',
        '20-瑞兰康保健品专营店')

    #设置完成状态
    app.set_finish()
