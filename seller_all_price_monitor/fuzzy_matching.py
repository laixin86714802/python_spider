#!/usr/bin/python
#coding:utf-8
import sys
reload (sys)
sys.setdefaultencoding('utf-8')

# Copyright (C) 2005-2016 All rights reserved.
# FILENAME:      fuzzy_matching.py
# VERSION:   1.0
# CREATED:   2016-11-8 16:18:34
# AUTHOR:    Planet margin
# DESCRIPTION:   8官网与健客比价，
#                算法：模糊匹配递归算法；
#                规则：(1)批准文号必须一致，(2)规格单位一致且不匹配字符2个之内，(3)名称正确率75%以上
# HISTORY: 
#*************************************************************
# 2016-11-11 23:11:59
import re
import time
import traceback
import conf.db_conf
import comm.PLog
from comm.db_helper import db_helper_class

# a = "惠氏 善存  多维元素片(29"
# b = "惠氏 善存银片 100"
# a = a.decode('utf-8')
# b = b.decode('utf-8')
# a = list(a)
# b = list(b)
# 药品名称字符串去空格,去(),两字符串中上限为12
# 药品名称模糊匹配算法使用递归实现，算法时间与空间复杂度较大
class Match(object):
    def __init__(self):
        # 数据库对象
        self.db_oper = db_helper_class(conf.db_conf)
        self.page_size = 20
        self.r_offset = 0


    def do_task(self):
        counts = 0
        count = 0
        while True:
            # 从数据库分页读取数据,助听器配件, YZB%
            # sql_first = '''select ProductCode, ProductName, Packing, OurPrice, ApprovalNumber 
            # from all_products where OurPrice != 0 and Packing !="" 
            # and ApprovalNumber not in ("无","","国食健字", "1", "XK16-108-5998", "test", "晶珠", "蓝帽", "0", 
            # "Q/WYX001-2008", "其他", "1234567", "20121213", "国妆特字", "卫消字号", "助听器配件")
            # and ApprovalNumber not like "%食%" and ApprovalNumber not like "%无%" and length(ApprovalNumber) > 9
            # and ApprovalNumber not like "%不%" and ApprovalNumber not like "%详见%" and ApprovalNumber not like "%QS%" 
            # and ApprovalNumber not like "%套餐%" and ApprovalNumber not like "%E+%" and ApprovalNumber not like "%消字%"
            # and ApprovalNumber not like "%xk%" and ApprovalNumber not like "%FD%" and ApprovalNumber not like "%Q/%"
            # and ApprovalNumber not like "YZB%" and ApprovalNumber not like "YZB/%" and ApprovalNumber not like "2016%" '''
            sql_first = '''select ProductCode, ProductName, Packing, OurPrice, ApprovalNumber 
            from all_products where OurPrice != 0 and Packing !="" 
            and length(ApprovalNumber) > 9 '''
            sql_second = '''limit %d offset %d''' % (self.page_size, self.r_offset)
            sql = sql_first + sql_second
            (line_cnt, tbl_datas) = self.db_oper.exe_search(sql)

            self.r_offset += self.page_size

            # 分页处理结束
            if line_cnt == 0:
                comm.PLog.Log("处理结束.")
                return
            # 取项
            for row_data in tbl_datas:
                counts += 1
                try:
                    product_name = row_data["ProductName"]
                    packing = row_data["Packing"]
                    approval_number = row_data["ApprovalNumber"]
                    product_name = product_name.replace(' ', '')
                    product_name = list(product_name.decode('utf-8'))
                    packing = list(packing.decode('utf-8'))
                    # 优化批准文号
                    approval_number = approval_number.replace(' ', '')
                    if "国药准字" in approval_number:
                        approval_number = re.sub("国药准字", "", approval_number)
                    else:
                        comm.PLog.Log("匹配目标: %s" % approval_number)
                        sql = "select id, shop_id,product_name,spec,product_price,approval_num from wrk_seller_all " \
                            '''where approval_num like "%%%s%%"''' % approval_number
                        (num, items) = self.db_oper.exe_search(sql)
                        if num == 0:
                            continue
                        # 匹配值
                        for item in items:
                            count += 1
                            match_spec = item["spec"]
                            match_product_name = item["product_name"]
                            match_product_price = item["product_price"]
                            match_product_name = match_product_name.replace(' ', '')
                            if match_product_price is None or match_product_price == 0:
                                continue
                            # 优化规格
                            if "％" in match_spec:
                                match_spec = re.sub("％", "%", match_spec)
                            elif "片" or "S" or "粒" in match_spec:
                                match_spec = re.sub("片" or "S" or "粒", "s", match_spec)
                            elif "ML" in match_spec:
                                match_spec = re.sub("ML", "ml", match_spec)
                            elif "CM" in match_spec:
                                match_spec = re.sub("CM", "cm", match_spec)
                            elif "克" or "G" in match_spec:
                                match_spec = re.sub("克" or "G", "g", match_spec)
                            elif "毫克" or "MG" in match_spec:
                                match_spec = re.sub("毫克" or "MG", "mg", match_spec)
                            # unicode编码
                            match_spec = list(match_spec.decode('utf-8'))
                            match_product_name = list(match_product_name.decode('utf-8'))
                            # 匹配规格
                            if match_spec == packing:
                                self.load_to_db(row_data=row_data, item=item)
                            else:
                                if len(match_spec) <= 10 and len(packing) <= 10:
                                    error_spec_char = self.cal(match_spec, packing)
                                elif len(match_spec) > 10 and len(packing) > 10:
                                    match_spec = match_spec[0:9]
                                    packing = packing[0:9]
                                    error_spec_char = self.cal(match_spec, packing)
                                elif len(match_spec) > 10 and len(packing) <= 10:
                                    match_spec = match_spec[0:9]
                                    error_spec_char = self.cal(match_spec, packing)
                                elif len(match_spec) <= 10 and len(packing) > 10:
                                    packing = packing[0:9]
                                    error_spec_char = self.cal(match_spec, packing)
                                if error_spec_char < 2:
                                    self.load_to_db(row_data=row_data, item=item)
                                elif error_spec_char > 1 and error_spec_char < 4:
                                    # 匹配名称
                                    if len(match_product_name) <= 10 and len(product_name) <= 10:
                                        error_product_name_char = self.cal(match_product_name, product_name)
                                    elif len(match_product_name) > 10 and len(product_name) > 10:
                                        match_product_name = match_product_name[0:9]
                                        product_name = product_name[0:9]
                                        error_product_name_char = self.cal(match_product_name, product_name)
                                    elif len(match_product_name) <= 10 and len(product_name) > 10:
                                        product_name = product_name[0:9]
                                        error_product_name_char = self.cal(match_product_name, product_name)
                                    elif len(match_product_name) > 10 and len(product_name) <= 10:
                                        match_product_name = match_product_name[0:9]
                                        error_product_name_char = self.cal(match_product_name, product_name)
                                    product_name_char = float(len(product_name))
                                    match_probability = error_product_name_char/product_name_char
                                    if match_probability > 0.6:
                                        self.load_to_db(row_data=row_data, item=item)
                            comm.PLog.Log("数目%s：总数%s" % (counts, count))

                except:
                    print traceback.format_exc()
    # 字符比较函数
    def compare(self, a, b):
        return a == b

    # 递归匹配函数
    def cal(self, str_1, str_2, ismatch=False, i=0, j=0):
        score = 0
        # 越界终止
        if (i >= len(str_1) or j >= len(str_2)):
            return False
        # 比较两字符是否相等
        ismatch = self.compare(str_1[i], str_2[j])
        if ismatch:
            score += 1
            # 如果一致对比下一个字符
            if (i+1 < len(str_1) and j+1 < len(str_2)):
                score += self.cal(str_1, str_2, ismatch, i=i+1, j=j+1)
        else:
            # 三种情况递归，空间复杂度(min(len(str_1),len(str_2),1+(max(len(str_1),len(str_2))-1))^3
            temp1 = 0
            temp2 = 0
            temp3 = 0
            temp1 += self.cal(str_1, str_2, ismatch, i=i, j=j+1)
            temp2 += self.cal(str_1, str_2, ismatch, i=i+1, j=j)
            temp3 += self.cal(str_1, str_2, ismatch, i=i+1, j=j+1)
            temp4 = max(temp1, temp2)
            score += max(temp3, temp4)
        return score

    # 入库函数
    def load_to_db(self, row_data, item):
        try:
            collecttime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(time.time())))
            match_id = item["id"]
            shop_id = item["shop_id"]
            product_code = row_data["ProductCode"]
            our_price = int(row_data["OurPrice"])/100.0
            other_price = float(item["product_price"])
            # 查重
            sql = "select id from wrk_shop_diff where shop_id='%s' and product_code='%s'" % (shop_id, product_code)
            (line_num, line_datas) = self.db_oper.exe_search(sql)
            if line_num == 0 and other_price < 2*our_price and our_price < 2*other_price:
                # 入库
                sql = "insert into wrk_shop_diff(match_id, shop_id, product_code, our_price, other_price, collect_time) values(%s, %s, %s, %s, %s, %s)"
                values = (
                    match_id,
                    shop_id,
                    product_code,
                    our_price,
                    other_price,
                    collecttime
                )
                self.db_oper.exe_insert(sql, values)
                comm.PLog.Log("入库成功.")
        except:
            print traceback.format_exc()

a = Match()
a.do_task()