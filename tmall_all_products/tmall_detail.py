# usr/bin/python
# -*-coding:utf-8-*-
# -------------------------------------------
# 无法加载价格区间
# 批准文号字段
import sys 
reload(sys) 
sys.setdefaultencoding("utf-8")

import re
import time
import chardet
import traceback
import requests
import HTMLParser

import comm.PLog
import conf.db_conf
import comm.random_useragent
from comm.db_helper import db_helper_class

class detail(object):

    def __init__(self):
        # 创建数据库对象
        self.db_oper = db_helper_class(conf.db_conf)
        # 分页大小
        self.page_size = 20
        # 读取偏移值
        self.r_offset = 0
        # 处理商品数
        self.curr_prog = 0
        # 商品入库数
        self.load_num = 0
        # 解析HTML字符实体
        self.html_analysis = HTMLParser.HTMLParser()

    def do_mian(self):
        self.last_list_jobid = '''%T%'''
        comm.PLog.Log("最新任务是%s" % (self.last_list_jobid))
        self.do_task(self.last_list_jobid)

    # 从list表中获取url等相关信息
    def do_task(self, task_id):
        # task_id = "68907729"
        state = "0"
        # sql = "select count(*) from tmall_list where sSource=%s and sState=%s" % (task_id, state)
        sql = "select count(*) from tmall_list where sState = '%s'" % state
        # 任务总量
        all_task_count = self.db_oper.get_count(sql)
        comm.PLog.Log("任务总量:%d" % all_task_count)
        while True:
            # 从数据库分页读取数据
            # sql = "select sSource, sTargetUrl, sProductId, sPrice"  \
            #     " from tmall_list where sSource=%s and sState=%s limit %d offset %d" % (
            #     task_id, state, self.page_size, self.r_offset)
            sql = "select sSource, sTargetUrl, sProductId, sPrice"  \
                " from tmall_list where sState = '%s' limit %d offset %d" % (
                state, self.page_size, self.r_offset)
            (line_cnt, tbl_datas) = self.db_oper.exe_search(sql)

            self.r_offset += self.page_size

            # 分页处理结束
            if line_cnt == 0:
                comm.PLog.Log("处理结束.")
                return
            # 处理list页内容
            for row_data in tbl_datas:
                try:
                    sSource = row_data["sSource"]
                    sTargetUrl = row_data["sTargetUrl"]
                    product_id = row_data["sProductId"]
                    sPrice = row_data["sPrice"]

                    comm.PLog.Log("--------------------------------------")
                    comm.PLog.Log("下载目标: %s" % sTargetUrl)

                    #判断是否已经下载
                    sql = "select product_id" \
                        " from tmall_detail where product_id='%s'" % (product_id)
                    rcd_cnt = self.db_oper.get_count(sql)
                    if rcd_cnt > 0:
                        comm.PLog.Log("已经存在，不再取!")
                        continue

                    comm.PLog.Log("已经下载数:%d" % (self.curr_prog))
                    # 停止2秒
                    # time.sleep(2)

                    comm.PLog.Log("当前请求地址: %s" % sTargetUrl)
                    user_agent = comm.random_useragent.getRandomUAItem()
                    # 获取商品源文件
                    html_headers = {
                     'User-Agent':user_agent,
                    }
                    # HTTP请求
                    html_req = requests.get(sTargetUrl,headers=html_headers,timeout=10)
                    # 返回源文件内容
                    html_content = html_req.content
                    # 获取商品js文件
                    # js_headers = {
                    #  'User-Agent':user_agent,
                    #  'Referer':sTargetUrl,
                    # }
                    # http = "https://mdskip.taobao.com/core/initItemDetail.htm?"
                    # param_1 = "household=false&isPurchaseMallPage=false&"
                    # param_2 = "cachedTimestamp=1476934403680&isRegionLevel=false&"
                    # param_3 = "itemId=%s&" % product_id
                    # param_4 = "isAreaSell=false&service3C=false&"
                    # param_5 = "isForbidBuyItem=false&isApparel=false&"
                    # param_6 = "isSecKill=false&queryMemberRight=true&"
                    # param_7 = "tryBeforeBuy=false&sellerPreview=false&"
                    # param_8 = "tmallBuySupport=true&offlineShop=false&"
                    # param_9 = "isUseInventoryCenter=false&addressLevel=2&"
                    # param_10 = "showShopProm=false&cartEnable=true&"
                    # param_11 = "callback=setMdskip&timestamp=1476934336073&"
                    # param_12 = "isg=AgQE-JfGVW0sYmwUkRmYt3j5XIj24yiF&"
                    # param_13 = "isg2=Ary8y2nSyEeoifPeV4WIql2Ug1rhTGDfYnYrL5Y9NqeIYV7rvMVnbjCTNxb0"
                    # url = http+param_1+param_2+param_3+param_4+param_5+param_6+ \
                    # param_7+param_8+param_9+param_10+param_11+param_12+param_13
                    # # js请求
                    # req_js = requests.get(url,headers=js_headers,timeout=10)
                    
                    # 返回js内容
                    # js_content = req_js.content

                    item = {}
                    item["sSource"] = sSource
                    item['fld_url'] = sTargetUrl
                    item['fld_product_id'] = product_id
                    item["fld_price_1"] = sPrice
                    item["fld_price_2"] = None

                    self.parse_detail(html_content=html_content, item=item)
                except:
                    traceback.print_exc()
    # 解析源文件和js文件内容
    def parse_detail(self, html_content, item):
        try:
            # 源文件网页转码utf-8
            content_type = chardet.detect(html_content)
            if content_type['encoding'] != "UTF-8":
                html_content = html_content.decode(content_type['encoding'], 'ignore')
                html_content = html_content.encode("utf-8", 'ignore')

            # 获取商品名
            title = r'''(?:<h1\sdata-spm="1000983">\s+)(?P<sTitle>.*?)(?:\s+</h1>)'''
            re_prodname = re.search(title, html_content, re.S | re.I)
            if re_prodname:
                item["fld_product_name"] = "".join(re_prodname.group("sTitle"))
            else:
                item["fld_product_name"] = ""

            # 获取批准文号|注册证号
            item["fld_approval_num"] = ""
            item["fld_register_num"] = ""
            re_approval = r'''(?:批准文号:&nbsp;)(?P<sAppRovalNum>[^<]*)(?:</li>)'''
            re_approval_num = re.search(re_approval, html_content, re.S | re.I)
            if re_approval_num:
                approval_num = re_approval_num.group("sAppRovalNum")
                # 解析HTML字符实体
                approval_num = self.html_analysis.unescape(approval_num)
                if "国药准字" in approval_num:
                    item["fld_approval_num"] = "".join(approval_num)
                else:
                    item["fld_register_num"] = "".join(approval_num)

            # 获取注册证号
            if item["fld_register_num"] == "":
                re_register = r'''(?:>注册证号:&nbsp;)(?P<sRegisterNum>[^<]*)(?:</li>)'''
                re_register_num = re.search(re_register, html_content, re.S | re.I)
                if re_register_num:
                    register_num = re_register_num.group("sRegisterNum")
                    # 解析HTML字符实体
                    register_num = self.html_analysis.unescape(register_num)
                    item["fld_register_num"] = register_num
                else:
                    item["fld_register_num"] = ""

            # js网页转码utf-8
            # content_type = chardet.detect(js_content)
            # if content_type['encoding'] != "UTF-8":
            #     js_content = js_content.decode(content_type['encoding'], 'ignore')
            #     js_content = js_content.encode("utf-8", 'ignore')

            # 获取月销量sellCount
            item["fld_month_sale_cnt"] = None
            # re_sell = r'''(?:"sellcount":)(?P<sellcount>\d+)'''
            # re_month_sale_cnt = re.search(re_sell, js_content, re.S | re.I)
            # if re_month_sale_cnt:
            #     item["fld_month_sale_cnt"] = "".join(re_month_sale_cnt.group("sellcount"))
            # else:
            #     item["fld_month_sale_cnt"] = None

            # 获取商品类型
            item["fld_proudect_type"] = "处方药"

            self.curr_prog += 1
            comm.PLog.Log("ID: %s" % (item['fld_product_id']))
            comm.PLog.Log("标题: %s" % (item["fld_product_name"]))
            comm.PLog.Log("价格: %s" % (item["fld_price_1"]))
            comm.PLog.Log("销量: %s" % (item["fld_month_sale_cnt"]))
            self.load_to_db(item)
        except:
            traceback.print_exc()

    # 存入数据库
    def load_to_db(self, item):

        comm.PLog.Log("目标入库数%d" % (self.load_num))
        try:
            fld_inserttime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(time.time())))
            sql = "insert into tmall_detail" \
                "(shop_id, product_id, product_name, sale_num_30," \
                " prm_price_min, prm_price_max, approval_num, register_num," \
                " product_url, collect_time, product_type)" \
                " values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            vals = (
                item["sSource"],  # shop_id
                item["fld_product_id"],
                item["fld_product_name"],
                item["fld_month_sale_cnt"],
                item["fld_price_1"],
                item["fld_price_2"],
                item["fld_approval_num"],
                item["fld_register_num"],
                item["fld_url"],
                fld_inserttime,
                item["fld_proudect_type"]
            )
            self.db_oper.exe_insert(sql, vals)
            comm.PLog.Log("完成.")
            self.load_num += 1
        except:
            traceback.print_exc()

a = detail()
a.do_mian()