#! urs/bin/python
# coding: utf-8


# 康爱多官网全量采集
import time
import re
import math
import comm.PLog
import comm.random_useragent
import conf.db_conf
from comm.db_helper import db_helper_class
import traceback
import comm.requests_pkg

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class kangaiduo(object):
    def __init__(self):
        # 数据库对象
        self.db_oper = db_helper_class(conf.db_conf)

    def get_url_first(self):
        try:
            # 获取url列表
            sql = '''select url from bas_seller_all where shop_name="康爱多"'''
            (get_num,get_item) = self.db_oper.exe_search(sql)
            # 遍历url列表
            for i in xrange(0,get_num):
                url = get_item[i]["url"]
                # 获取页码
                (http_ok, resp) = comm.requests_pkg.get(url, max_try=5)
                if http_ok:
                    html = resp.content
                    # 读取商品个数
                    re_detail_num = '''(?:<span\sclass="first">.*?)(?P<detailNum>\d+)(?:.*?<)'''
                    detail_num = re.search(re_detail_num, html, re.S | re.I)
                    if detail_num:
                        detail_num = int(detail_num.group("detailNum"))
                    else:
                        continue
                    # 计算出页数
                    page = int(math.ceil(detail_num/20.0))
                self.do_main(url, page)
        except:
            print traceback.format_exc()

    def do_main(self, url, page_num):
        item = {}
        try:
            for i in xrange(1, page_num + 2):
                # 遍历商品列表页
                get_url = re.sub(r'''page=\d+''',"page=" + str(i), url)
                (http_ok, resp) = comm.requests_pkg.get(get_url, max_try=5)
                if http_ok:
                    html = resp.content
                    # 去噪
                    re_really = '''<ul\sid="YproductList">.*?<a\sclass="Yfirst"'''
                    re_detail_list = re.findall(re_really, html, re.S | re.I)
                    if re_detail_list:
                        resp_body = re_detail_list[0]
                    else:
                        continue
                    # 获取商品项
                    re_detail = '''(?:<p\sclass="Ypic">)(?P<detail>.*?)(?:<p\sclass="Yhave"><span></span></p>)'''
                    get_detail = re.compile(re_detail, re.S | re.I)
                    detail_list = get_detail.findall(resp_body)

                    # 解析商品
                    for deatil_item in detail_list:
                        # 获取url
                        item["prod_url"] = ""
                        re_url = '''(?:<a\shref=")(?P<url>.*?)(?:")'''
                        get_url = re.search(re_url, deatil_item, re.S | re.I)
                        if get_url:
                            product_uri = get_url.group("url")
                            url_real = "http://www.360kad.com%s" % str(product_uri)
                            item["prod_url"] = url_real

                        # 获取产品ID
                        item["prod_id"] = ""
                        re_detail_id = '''/(\d+).'''
                        get_detail_id = re.findall(re_detail_id, product_uri, re.S | re.I)
                        if get_detail_id:
                            product_id = get_detail_id[0]
                            item["prod_id"] = product_id

                        # 产品查重
                        sql = '''select id from `wrk_seller_all` where product_id="%s" and shop_id="100002"''' % product_id
                        (get_num,get_item) = self.db_oper.exe_search(sql)
                        if get_num > 0:
                            comm.PLog.Log("商品重复")
                            continue

                        # 竞争对手名称(康爱多)
                        item["shop_id"] = "100002"

                        # 产品名称
                        item["prod_name"] = ""
                        re_prod_name = '''(?:<a\shref=".*?alt=")(?P<name>.*?)(?:"\s)'''
                        get_prod_name = re.search(re_prod_name, deatil_item, re.S | re.I)
                        if get_prod_name:
                            item["prod_name"] = get_prod_name.group("name").strip()

                        # 价格
                        item["prod_price"] = None
                        re_price = '''(?:<span\sclass="RMB">￥)(?P<price>\d+|\d+.\d+)(?:</span>)'''
                        get_price = re.search(re_price, deatil_item, re.S | re.I)
                        if get_price:
                            item["prod_price"] = get_price.group("price")

                        # 获取详情
                        self.get_detail(item)
                        comm.PLog.Log("当前页数:%s" % i)
        except:
            print traceback.format_exc()

    # 请求url获取批准文号，规格
    def get_detail(self, item):
        try:
            url_detail = item["prod_url"]
            (http_ok, resp) = comm.requests_pkg.get(url_detail, max_try=5)
            if http_ok:
                # 去噪
                re_table = '''(?:<ul\sclass="clearfix">\s*)(?P<detail><li>商品名称.*?)(?:</ul>)'''
                get_table = re.search(re_table, resp.content, re.S | re.I)
                if get_table:
                    table_item = get_table.group("detail")
                    # 产品名称
                    if item["prod_name"] == "":
                        re_prod_name = '''(?:<li>商品名称：)(?P<name>.*?)(?:</li>)'''
                        get_prod_name = re.search(re_prod_name, table_item, re.S | re.I)
                        if get_prod_name:
                            item["prod_name"] = get_prod_name.group("name").strip()
                    # 获取批准文号
                    item["approval_num"] = ""
                    re_approval_num = '''(?:<li>批准文号：)(?P<approval>.*?)(?:</li>)'''
                    get_approval = re.search(re_approval_num, table_item, re.S | re.I)
                    if get_approval:
                        item["approval_num"] = get_approval.group("approval")
                    # 获取规格
                    item["spec"] = ""
                    re_spec = '''(?:<li>规格：)(?P<spec>.*?)(?:</li>)'''
                    get_spec = re.search(re_spec, table_item, re.S | re.I)
                    if get_spec:
                        item["spec"] = get_spec.group("spec")
                    # 获取产地
                    item["prod_place"] = ""
                    re_prod_place = '''(?:<li>生产企业：)(?P<prod_place>.*?)(?:</li>)'''
                    get_prod_place = re.search(re_prod_place, table_item, re.S | re.I)
                    if get_prod_place:
                        item["prod_place"] = get_prod_place.group("prod_place")
                    comm.PLog.Log("产品名称:%s" % item["prod_name"])
                    comm.PLog.Log("产品价格:%s" % item["prod_price"])

                    self.load_to_db(item)
        except:
            print traceback.format_exc()

    def load_to_db(self, item):
        try:
            collecttime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(time.time())))
            sql = "insert into wrk_seller_all(shop_id, product_id, product_name, approval_num, spec, product_place, product_price, product_url, collect_time) values(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            vals = (
                item["shop_id"],
                item["prod_id"],
                item["prod_name"],
                item["approval_num"],
                item["spec"],
                item["prod_place"],
                item["prod_price"],
                item["prod_url"],
                collecttime
                )
            self.db_oper.exe_insert(sql, vals)
            comm.PLog.Log("入库成功.")
        except :
            print traceback.format_exc()

a = kangaiduo()
a.get_url_first()