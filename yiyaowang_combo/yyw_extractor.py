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
    # 获取单品价格
    detail_singleprice = r'''(?:"price"\s*:\s*")(?P<sSinglePrice>\d+|\d+.\d+)(?:",)'''

    # 获取item_id
    detail_item_id = r'''(?:var\s*item_id\s*=\s*')(?P<sItemId>\d+)(?:';)'''

    # 获取materialtype
    detail_materialtype = r'''(?:var\s*materialtype\s*=\s*')(?P<sMaterialtype>\w+)(?:';)'''

    # 获取壹药网官方的内部的产品编号, 用于AJAX
    detail_productno = r'''(?:\[{"WareCode":")(?P<sProductNo>\d+)(?:",)'''

    # 套装Block块
    detail_tangzhuang_block = r'''(?P<sPrmBlock>PrmName":".*?"KitPrice":[\d\.]+)'''

    # 壹药网套装
    detail_tangzhuang_info = r'''(?:PrmName":")(?P<sPrmName>[^"]*?)(?:".*?"KitPrice":)(?P<sPrmPrice>[\d\.[=]+)'''

    # 可使用天数
    detail_usedDay = r'''(?:<input\sid="h_usedDay"\stype="hidden"\svalue=')(?P<sUserDay>\d+)'''

    # 疗程装信息块
    detail_treatment_info = r'''(?:{".*?productName":")(?P<sProductName>.*?)(?:".*?originalPrice":)(?P<sDetailCount>[\d\.]+)(?:,".*?detailCount":)(?P<sNumber>\d+)(?:,)'''

# PrmCode  编码
# PrmName  名称
# PrmTheme  
# PrmDesc
# PrmSubtitle  副标题
# KitWareQty  套餐数量
# KitPrice  套餐价格
# RxType  疗程
# OriginPrice  初始价
# HasRx  是否有货
# kitSubList  副标题中其他商品列表

# WareCode  商品标号
# Qty  数量
# Price  价格
# KitValue  套餐价


