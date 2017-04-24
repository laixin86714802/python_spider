#!/usr/bin/python
#coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 tmall_all_products_list_main.py
# VERSION: 	 1.0
# CREATED: 	 2016-07-21 15:45
# AUTHOR: 	 xuexiang
# DESCRIPTION: 
#
# HISTORY: 
#*************************************************************

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from tmall_all_products_list_class import tmall_all_products_list_class

if __name__ == '__main__':

    app = tmall_all_products_list_class()

    
    app.do_main(
        'https://ytrdyf.tmall.com/category.htm?search=y&orderType=hotsell_desc&pageNo=1',
        '103992228',
        '10-叶同仁大药房旗舰店')
        # 'https://huatuodyf.tmall.com/category.htm?search=y&orderType=hotsell_desc&pageNo=1',
        # '70324298',
        # '09-华佗大药房旗舰店')
        # 'https://oumulong.tmall.com/category.htm?search=y&orderType=hotsell_desc&pageNo=1',
        # '110907163',
        # '*08-欧姆龙官方旗舰店')
        # 'https://durex.tmall.com/category.htm?search=y&orderType=hotsell_desc&pageNo=1',
        # '108702391',
        # '*07-durex杜蕾斯官方旗舰店')
        # 'https://jianke.tmall.com/category.htm?search=y&orderType=hotsell_desc&pageNo=1',
        # '67371489',
        # '06-健客大药房旗舰店')
        # 'https://zuiqingfeng.tmall.com/category.htm?search=y&orderType=hotsell_desc&pageNo=1',
        # '116576560',
        # '*05-醉清风旗舰店')
        # 'https://haohushi.tmall.com/category.htm?search=y&orderType=hotsell_desc&pageNo=1',
        # '113500481',
        # '*04-好护士器械旗舰店')
        # 'https://yuyuegf.tmall.com/category.htm?search=y&orderType=hotsell_desc&pageNo=1',
        # '112174596',
        # '*03-鱼跃官方旗舰店')
        # 'https://yihaodayaofang.tmall.com/category.htm?search=y&orderType=hotsell_desc&pageNo=1',
        # '68982189',
        # '02-壹号大药房旗舰店')
        # 'https://kangaiduo.tmall.com/category.htm?search=y&orderType=hotsell_desc&pageNo=1',
        # '68907729',
        # '01-康爱多旗舰店')

