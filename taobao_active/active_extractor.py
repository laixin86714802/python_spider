#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 T001_Extractor.py
# VERSION: 	 1.0
# CREATED: 	 2016-01-06 21:01
# AUTHOR: 	 xuexiang
# DESCRIPTION:   规则提取器
#
# HISTORY:
#*************************************************************


class CommExtractor:
    # 承载页面去噪
    payload_puredata = r'''(?:<div\sclass="qg-category-list")(?P<sReserver>.*?)(?:<div\sid="J_Aside")'''

    # 产品总数量: 用于告警
    payload_productcnt = r'''(?:data-count=")(?P<sProductCount>\d+)'''

    # 已经抢光的产品
    payload_record_block_left0 = r'''(?:<div\sclass="qg-item\sqg-done">)(?P<sRecordBlock>.*?)(?:</div>\s+</div>\s+</div>)'''
    payload_record_info_left0 = r'''(?:<p\sclass="des">)(?P<sTitle>[^<]*?)(?:</p>\s+<p\sclass="subtitle">)(?P<sSubTitle>[^<]*?)(?:<.*?<span\sclass="promo-price">.*?<em>)(?P<sPrice>\d+)(?:.*?分抢光)(?P<sNum>\d+)'''

    # 没有抢光的产品
    payload_record_block_left99 = r'''(?P<sRecordBlock><a[^>]*?class="qg-item\sqg-ing".*?</div>\s+</div>\s+</a>)'''
    payload_record_info_left99 = r'''(?:href=")(?P<sUrl>[^"]*?)(?:".*?src=")(?P<sThumbImg>[^"]*?)(?:".*?<p\sclass="des">)(?P<sTitle>[^<]*?)(?:</p>\s+<p\sclass="subtitle">)(?P<sSubTitle>[^<]*?)(?:<.*?<span\sclass="promo-price">.*?<em>\s*)(?P<sPrice>\d+)(?:.*?已抢购)(?P<sRete>\d+%)(?:.*?已抢)(?P<sNum>\d+)(?:件)'''

    # 还没有开抢的产品
    payload_record_block_notbegin = r'''(?:<a.*?qg-item)(?P<sRecordBlock>.*?)(?:</a>)'''
    payload_record_info_notbegin = r'''(?:href=")(?P<sUrl>[^"]*?)(?:".*?src=")(?P<sThumbImg>[^"]*?)(?:".*?<p\sclass="des">)(?P<sTitle>[^<]*?)(?:</p>\s+<p\sclass="subtitle">)(?P<sSubTitle>[^<]*?)(?:<.*?<span\sclass="promo-price">.*?<em>\s*)(?P<sPrice>\d+)'''
