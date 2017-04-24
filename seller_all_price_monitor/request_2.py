#! urs/bin/python
# coding: utf-8


# 康德乐官网全量采集
import time
import re
import comm.PLog
import comm.random_useragent
import conf.db_conf
from comm.db_helper import db_helper_class
import traceback
import comm.requests_pkg
import chardet

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class kangdele(object):
    def __init__(self):
        # 数据库对象
        self.db_oper = db_helper_class(conf.db_conf)

    def get_url_first(self):
        try:
            # 获取url列表
            sql = '''select url from bas_seller_all where shop_name="康德乐"'''
            (get_num,get_item) = self.db_oper.exe_search(sql)
            print "1"
            # 遍历url列表
            for i in xrange(0,get_num):
                url = get_item[i]["url"]
                # 获取页码
                (http_ok, resp) = comm.requests_pkg.get(url, max_try=5)
                if http_ok:
                    html = resp.content
                    re_page = '''(?:<div\sclass="page_b">.*?/)(?P<page>\d+)(?:</div>)'''
                    page = re.search(re_page, html, re.S | re.I)
                    page_num = int(page.group("page"))
                self.do_main(url, page_num)
        except:
            print traceback.format_exc()

    def do_main(self, url, page_num):
        item = {}
        try:
            for i in xrange(1, page_num + 2):
                # 遍历商品列表页
                get_url = re.sub(r'''b0-(\d+)-1-2.html''',"b0-" + str(i) + "-1-2.html", url)
                (http_ok, resp) = comm.requests_pkg.get(get_url, max_try=5)
                print "----"
                if http_ok:
                    html = resp.content
                    # 去噪
                    re_really = '''<div\sclass="prorig_product_list">.*?<div\sclass="page_a">'''
                    re_detail_list = re.findall(re_really, html, re.S | re.I)
                    resp_body = re_detail_list[0]
                    print chardet.detect(resp_body)
                    return
        except:
            pass
            