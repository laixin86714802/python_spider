#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 T001_Extractor.py
# VERSION: 	 1.0
# CREATED: 	 2016-01-06 21:01
# AUTHOR: 	 xuexiang
# DESCRIPTION:   T001规则提取器
#
# HISTORY:
#*************************************************************


class CommExtractor:
    # 承载页面去噪
    payload_puredata = r'''(?:<div\sclass="J_TItems">)(?P<sReserve>.*?)(?:<div\sclass="comboHd">)'''

    # 承载页面中的记录块(对应于一个商品)
    payload_record_block = r'''(?P<sRecord><dl\s+class="item\s(?:last)?".*?</dl>)'''

    # 承载页提取每种商品信息
    payload_record_info = r'''(?:<dl\sclass="item\s(?:last)?"\sdata-id=")(?P<fld_productid>\d+)(?:">.*?<a\sclass="item-name".*?href=")(?P<fld_url>[^"]*?)(?:"[^>]*?>)(?P<fld_caption>[^<]*?)(?:</a>.*?<span\sclass="c-price">)(?P<fld_price>[\d\.]+)'''

    # 承载顺序翻页
    payload_nextpage = r'''(?:<a\sclass="J_SearchAsync\snext"\shref=")(?P<sUrl>[^"]*?)(?:")'''

    # 页面总量预测
    payload_pagecount = r'''(?:<b\sclass="ui-page-s-len">\d/)(?P<sPageCount>\d+)(?:</b>)'''

    ##########################################################################

    # 目标页：产品参数去噪
    target_puredata = r'''(?:<ul\sid="J_AttrUL">)(?P<sReserve>.*?)(?:</ul>)'''
