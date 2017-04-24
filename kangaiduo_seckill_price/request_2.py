#!/usr/bin/python
#coding:utf-8

import re
import conf.db_conf
import comm.PLog
import comm.requests_pkg
from comm.db_helper import db_helper_class

class Match(object):
    def __init__(self):
        # 数据库对象
        self.db_oper = db_helper_class(conf.db_conf)

    def do_task(self):
            # 从数据库分页读取数据
            sql = "SELECT comp_prod_id FROM `bas_comweb_url` where comp_id=100002"
            (line_cnt, data_set) = self.db_oper.exe_search(sql)
            comm.PLog.Log("当前异常监控记录数=%d" % line_cnt)
            count = 0
            for data_row in data_set:
                count += 1
                #产品价格
                fld_prod_id = data_row["comp_prod_id"]
                url = "http://www1.360kad.com/Topic/ProductList?wareSkuCodes=" + str(fld_prod_id)
                (http_ok, resp) = comm.requests_pkg.get(url, max_try=5)
                if http_ok:
                    html = resp.content
                    re_prod_price = '''(?:"PrmPrice":)(?P<prod_id>\d+|\d+.\d+)(?:,)'''
                    prod_price = re.search(re_prod_price, html, re.S | re.I)
                    if prod_price:
                        page_num = prod_price.group("prod_id")
                        string = str(fld_prod_id) + ":" + str(page_num) + '\n'
                        if page_num != "0":
                            open("a.txt", "ab").write(string)
                print count
a = Match()
a.do_task()