#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 pm_parse_class.py
# VERSION: 	 1.0
# CREATED: 	 2016-03-09 15:08
# AUTHOR: 	 xuexiang
# DESCRIPTION:   网页解析类库
#
# HISTORY:
#*************************************************************
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import re
import params_conf
import comm.PLog
import comm.stone_funs
import comm.requests_pkg
from comm.MyHttpDownFailed import MyHttpDownFailed
from comm.MyHttpParseFailed import MyHttpParseFailed


class pm_parse_class():

    # 键客网
    @staticmethod
    def parse_jkw(prod_id, url):
        (html_ok, html_resp) = comm.requests_pkg.get(
            url, params_conf.max_http_retry_cnt)
        if not html_ok:
            raise MyHttpDownFailed()

        # 转换为UTF8编码
        html_content = comm.stone_funs.ToUtf8(html_resp.content)
        re_price = re.search(
            r'''(?:<em\sclass="f20">)(?P<sPrice>[\d\.]+)(?:</em></span>)''',
            html_content,
            re.S | re.I)
        if re_price == None:
            raise MyHttpParseFailed()

        fld_prod_price = float(re_price.group("sPrice"))
        return fld_prod_price

    # 壹药网
    @staticmethod
    def parse_yyw(prod_id, url):
        (html_ok, html_resp) = comm.requests_pkg.get(
            url, params_conf.max_http_retry_cnt)
        if not html_ok:
            raise MyHttpDownFailed()

        # 转换为UTF8编码
        html_content = comm.stone_funs.ToUtf8(html_resp.content)

        re_price = re.search(
            r'''(?:"price"\s*:\s*")(?P<sPrice>[\d\.]+)(?:")''',
            html_content,
            re.S | re.I)
        if re_price == None:
            raise MyHttpParseFailed()

        # 产品价格
        fld_prod_price = float(re_price.group("sPrice"))
        return fld_prod_price

    # 康爱多
    @staticmethod
    def parse_kad(prod_id, url):
        (html_ok, html_resp) = comm.requests_pkg.get(
            url, params_conf.max_http_retry_cnt)
        if not html_ok:
            raise MyHttpDownFailed()

        # 转换为UTF8编码
        html_content = comm.stone_funs.ToUtf8(html_resp.content)

        re_price = re.search(
            r'''(?:salePrice\s*:\s*)(?P<sPrice>[\d\.]+)(?:,)''',
            html_content,
            re.S | re.I)
        if re_price == None:
            raise MyHttpParseFailed()

        fld_prod_price = float(re_price.group("sPrice"))
        return fld_prod_price

    # 康德乐
    @staticmethod
    def parse_kdl(prod_id, url):
        (html_ok, html_resp) = comm.requests_pkg.get(
            url, params_conf.max_http_retry_cnt)
        if not html_ok:
            raise MyHttpDownFailed()

        # 转换为UTF8编码
        html_content = comm.stone_funs.ToUtf8(html_resp.content)

        re_price = re.search(
            r'''(?:id="ECS_SHOPPRICE">.*?</em>)(?P<sPrice>[\d\.]+)''',
            html_content,
            re.S | re.I)
        if re_price == None:
            raise MyHttpParseFailed()

        fld_prod_price = float(re_price.group("sPrice"))
        return fld_prod_price

    # 健一网
    @staticmethod
    def parse_jyw(prod_id, url):
        (html_ok, html_resp) = comm.requests_pkg.get(
            url, params_conf.max_http_retry_cnt)
        if not html_ok:
            raise MyHttpDownFailed()

        # 转换为UTF8编码
        html_content = comm.stone_funs.ToUtf8(html_resp.content)

        re_price = re.search(
            r'''(?:discount_price.*?value=")(?P<sPrice>[\d\.]+)''',
            html_content,
            re.S | re.I)
        if re_price == None:
            raise MyHttpParseFailed()

        fld_prod_price = float(re_price.group("sPrice"))
        return fld_prod_price

    # 老百姓
    @staticmethod
    def parse_lbx(prod_id, url):
        (html_ok, html_resp) = comm.requests_pkg.get(
            url, params_conf.max_http_retry_cnt)
        if not html_ok:
            raise MyHttpDownFailed()

        # 转换为UTF8编码
        html_content = comm.stone_funs.ToUtf8(html_resp.content)

        re_price = re.search(
            r'''(?:lblPrice">)(?P<sPrice>[\d\.]+)''',
            html_content,
            re.S | re.I)
        if re_price == None:
            raise MyHttpParseFailed()

        fld_prod_price = float(re_price.group("sPrice"))
        return fld_prod_price

    # 亿生康
    @staticmethod
    def parse_ysk(prod_id, url):
        (html_ok, html_resp) = comm.requests_pkg.get(
            url, params_conf.max_http_retry_cnt)
        if not html_ok:
            raise MyHttpDownFailed()

        # 转换为UTF8编码
        html_content = comm.stone_funs.ToUtf8(html_resp.content)

        re_price = re.search(
            r'''(?:id="promote_price".*?>\s+)(?P<sPrice>[\d\.]+)(?:</i>)''',
            html_content,
            re.S | re.I)
        if re_price == None:
            raise MyHttpParseFailed()

        fld_prod_price = float(re_price.group("sPrice"))
        return fld_prod_price

    # 云开
    @staticmethod
    def parse_yk(prod_id, url):
        (html_ok, html_resp) = comm.requests_pkg.get(
            url, params_conf.max_http_retry_cnt)
        if not html_ok:
            raise MyHttpDownFailed()

        # 转换为UTF8编码
        html_content = comm.stone_funs.ToUtf8(html_resp.content)

        re_price = re.search(
            r'''(?:price">)(?P<sPrice>[\d\.]+)''',
            html_content,
            re.S | re.I)
        if re_price == None:
            raise MyHttpParseFailed()

        fld_prod_price = float(re_price.group("sPrice"))
        return fld_prod_price

    # 康之家
    @staticmethod
    def parse_kzj(prod_id, url):
        (html_ok, html_resp) = comm.requests_pkg.get(
            url, params_conf.max_http_retry_cnt)
        if not html_ok:
            raise MyHttpDownFailed()

        # 转换为UTF8编码
        html_content = comm.stone_funs.ToUtf8(html_resp.content)

        re_price = re.search(
            r'''(?:<em\sid="rprice">)(?P<sPrice>[\d\.]+)''',
            html_content,
            re.S | re.I)
        if re_price == None:
            raise MyHttpParseFailed()

        fld_prod_price = float(re_price.group("sPrice"))
        return fld_prod_price
