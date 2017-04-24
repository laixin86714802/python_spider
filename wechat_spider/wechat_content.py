# !/usr/bin/python
# -*- coding: utf-8 -*-

import math
import time
import re
import random
import comm.PLog
import comm.random_useragent
import conf.db_conf
from comm.db_helper import db_helper_class
import traceback
import comm.requests_pkg
import requests
# from comm.random_useragent import getRandomCookie
# from comm.random_useragent import getRandomIP
import calendar as cal
import os

class wechat_get_content(object):
    def __init__(self):
        # 数据库对象
        self.db_oper = db_helper_class(conf.db_conf)
        # 原创标识
        self.original_word = '''<span\sid="copyright_logo"\sclass="rich_media_meta\smeta_original_tag">原创</span>'''
        # 简介
        self.intro = '''(?:<p\sclass="txt-info".*?>)(?P<intro>.*?)(?:</p>)'''
        # cookie设置
        self.cookie = {"SUV":"00175E2BDA6B097D57CBCDBE7DA71981",
        "IPLOC":"CN4401",
        "CXID":"860E089DD32C47EE1ECF55ED807B8483",
        "weixinIndexVisited":"1",
        "Hm_lvt_96d9d92b8a4aac83bc206b6c9fb2844a":"1474170419,1474181444",
        "pgv_pvi":"5441667072",
        "m":"3B3BF1EE5348A83F1126D107D0679A9B",
        "GOTO":"Af99046",
        "ld":"1kllllllll2gc8WVQx31FOkMUKPY9rSnLu7JKyllll9lllll4klll5@@@@@@@@@@",
        "ad":"IZllllllll2g8FjPlllllVkcVMklllllLu7JKyllllklllllpqxlw@@@@@@@@@@@",
        "SUID":"7D096BDA3320910A0000000057CD2EFF",
        "YYID":"3B3BF1EE5348A83F1126D107D0679A9B",
        "ABTEST":"6|1480328071|v1",
        "SNUID":"176301B06A6F2830D6BC3C936AE5FEE5",
        "SUIR":"176301B06A6F2830D6BC3C936AE5FEE5",
        "ppinf":"5|1480472199|1481681799|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZTo0NTolRTYlQTElOTElRTQlQkIlQTMlRTUlODUlOEIlRTclOUElODQlRTclOEMlQUJ8Y3J0OjEwOjE0ODA0NzIxOTl8cmVmbmljazo0NTolRTYlQTElOTElRTQlQkIlQTMlRTUlODUlOEIlRTclOUElODQlRTclOEMlQUJ8dXNlcmlkOjQ0OjBGRUY3RjYyNURFRURDNENENTQ1QTQzRUVGM0NGN0I1QHFxLnNvaHUuY29tfA",
        "pprdig":"RiQVGnfvU914niX77Vxk8xtJThF_ux3DA7UjmVNJrxBwrzpx6CWo38ZIEm4AfXZ3Ez6dKMnwA0pj3kXHiP8-Qytg8HVJfNCd0NwWrGOjgLT3CHcQtHeHy7oqhJhwGtjlIqataNhNA-JbcH6KTtliGMwLlDw7GmF_Odfl0Wz7JQE",
        "JSESSIONID":"aaa-ISi7b1d8ufz7S_UIv",
        "sct":"45",
        "usid":"NNV9tIXWQrAUgBuz",
        "clientId":"3A41D977ADC76C0D1A18D0A0AC666DB9",}

    def get_proxies(self):
        # 阿布云代理服务器
        proxyHost = "proxy.abuyun.com"
        proxyPort = "9010"

        # 代理隧道验证信息
        proxyUser = "H1F46KFI5PG8TGDD"
        proxyPass = "51AABFBCFCB6B729"

        proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
            "host" : proxyHost,
            "port" : proxyPort,
            "user" : proxyUser,
            "pass" : proxyPass,
        }

        proxies = {
            "http"  : proxyMeta,
            "https" : proxyMeta,
        }
        return proxies


    def get_url_first(self):
        try:
            item = {}
            # 获取关键词列表
            sql = '''SELECT `channel`, `catId`, `keyword` FROM tb_wechat_table'''
            (get_num,get_item) = self.db_oper.exe_search(sql)
            # 设置初始页数为1
            page = 2
            # 遍历关键词列表
            for i in xrange(0,get_num):
                # 获取频道、栏目ID、关键词
                item["channel"] = get_item[i]["channel"]
                item["catId"] = get_item[i]["catId"]
                item["keyword"] = get_item[i]["keyword"]
                # 按年月全文搜索文章(时间频率为每个月,类型为图集)
                date_mould = "%d-%s-%s"
                year = [2014, 2015, 2016]
                for every_year in year:
                    for m in range(1, 13):
                        d = cal.monthrange(every_year, m)
                        if m <10:
                            month = "0" + str(m)
                        else:
                            month = str(m)
                        start_month = date_mould % (every_year, month, "01")
                        end_month = date_mould % (every_year, month, d[1])
                        url = "http://weixin.sogou.com/weixin?type=2&ie=utf8&query=%s&tsn=5&ft=%s&et=%s&interation=458754&wxid=&usip=null&from=tool" % (item["keyword"], start_month, end_month)
                        proxies = self.get_proxies()
                        resp = requests.get(url, cookies=self.cookie, proxies=proxies)
                        print "start: ", url
                        print "IP_1:",proxies
                        # time.sleep(10)
                        # 频繁访问
                        re_visit = "您的访问过于频繁"
                        get_visit = re.findall(re_visit, resp.content, re.S | re.I)
                        if get_visit:
                            print "!!!!!!!!Visit Often!!!!!!!!"
                            break
                        # 获取页数
                        re_page = '''(?:<div\sclass="mun">找到约)(?P<page>.*?)(?:条结果)'''
                        get_page = re.search(re_page, resp.content, re.S | re.I)
                        if get_page:
                            page_all = get_page.group("page")
                            page_all = int(page_all.replace(',',''))
                            if page_all/10.0 > 1:
                                page = int(math.ceil(page_all/10.0)) + 1
                                if page > 101:
                                    page = 101
                            else:
                                page = 2
                            # 提交至列表页
                            print "page:%d" % page
                            self.get_list_content(page=page,item=item, url=url)
        except:
            print traceback.format_exc()
    # 获取列表详情
    def get_list_content(self, page, item, url):
        try:
            # 获取url
            for j in range(1, page):
                url = url + "&page=%d" % j
                proxies = self.get_proxies()
                resp = requests.get(url, cookies=self.cookie, proxies=proxies)
                print "IP_2:", proxies
                # time.sleep(10)
                html = resp.content
                # 获取该页10个标题
                re_detail = '''<div\sclass="txt-box">.*?</div>'''
                get_detail = re.compile(re_detail, re.S | re.I)
                detail_list = get_detail.findall(html)
                # 计数
                count = 0
                # 分段解析
                for deatil_item in detail_list:
                    # time.sleep(5)
                    count += 1
                    # 获取url
                    re_url = '''(?:<a\starget="_blank"\shref=")(?P<url>.*?)(?:")'''
                    get_url = re.search(re_url, deatil_item, re.S | re.I)
                    # 获取简介
                    re_intro = '''(?:<p\sclass="txt-info".*?>)(?P<intro>.*?)(?:</p>)'''
                    get_intro = re.search(re_intro, deatil_item, re.S | re.I)
                    item["intro"] = ""
                    if get_intro:
                        item["intro"] = get_intro.group("intro")
                        item["intro"] = item["intro"].replace('<em><!--red_beg-->','')
                        item["intro"] = item["intro"].replace('<!--red_end--></em>','')
                    if get_url:
                        print "key:%s, page:%s, count:%d" % (item["keyword"], j, count)
                        detail_url = get_url.group("url")
                        detail_url = detail_url.replace('&amp;','&')
                        # 获取文章详情
                        proxies = self.get_proxies()
                        resp = requests.get(detail_url, cookies=self.cookie, proxies=proxies)
                        print "IP_3:", proxies
                        print "Get the html detail"
                        # time.sleep(10)
                        detail_html = resp.content
                        # 获取公共号
                        re_source = '''(?:<label\sclass="profile_meta_label">微信号</label>\s+<span\sclass="profile_meta_value">)(?P<source>.*?)(?:</span>)'''
                        get_source = re.search(re_source, detail_html, re.S | re.I)
                        item["source"] = ""
                        if get_source:
                            item["source"] = get_source.group("source")
                        # 获取标题
                        re_title = '''(?:<title>)(?P<title>.*?)(?:</title>)'''
                        get_title = re.search(re_title, detail_html, re.S | re.I)
                        item["title"] = ""
                        if get_title:
                            item["title"] = get_title.group("title").strip()
                        # 获取正文
                        re_content = '''<div\sclass="rich_media_content.*?</div>'''
                        get_content = re.findall(re_content, detail_html, re.S | re.I)
                        if get_content:
                            wechat_content = get_content[0]
                            wechat_content = wechat_content.replace('data-src','src')
                            # 正文编码
                            wechat_content = wechat_content.decode("utf-8", 'ignore')
                            wechat_content = wechat_content.encode("GB2312", 'ignore')
                        # 验证原创
                        item["original"] = 0
                        original = re.findall(self.original_word, detail_html, re.S | re.I)
                        # keyword编码utf-8, 作为文件夹名
                        keyword = item["keyword"]
                        title = item["title"]
                        keyword = keyword.encode("GB2312", 'ignore')
                        title = title.decode("utf-8", 'ignore')
                        title = title.encode("GB2312", 'ignore')
                        if original:
                            print "**********Original content is got**********"
                            item["original"] = 1
                            # 写入文件
                            m_outpath = "E:\\wechat_article\\original\\%s\\%s" % (str(item["channel"]), keyword)
                            if(not(os.path.exists(m_outpath))):
                                os.mkdir(m_outpath)
                            uri = "E:\\wechat_article\\original\\%s\\%s\\%s.html" % (str(item["channel"]), keyword, title)
                            f = open(uri, "wb")
                            f.write(wechat_content)
                            f.close()
                        else:
                            print "It is not original"
                            # 写入文件
                            m_outpath = "E:\\wechat_article\\not_original\\%s\\%s" % (str(item["channel"]), keyword)
                            if(not(os.path.exists(m_outpath))):
                                os.mkdir(m_outpath)
                            uri = "E:\\wechat_article\\not_original\\%s\\%s\\%s.html" % (str(item["channel"]), keyword, title)
                            f = open(uri, "wb")
                            f.write(wechat_content)
                            f.close()
                        # 入库
                        self.load_to_db(item)
        except:
            print traceback.format_exc()
  
    def load_to_db(self, item):
        try:
            collecttime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(time.time())))
            sql = '''insert into wechat_detail(`channel`,`catId`,`keyword`,`source`,`title`,`intro`,`original`, collect_time) values(%s, %s, %s, %s, %s, %s, %s, %s)'''
            vals = (
                item["channel"],
                item["catId"],
                item["keyword"],
                item["source"],
                item["title"],
                item["intro"],
                item["original"],
                collecttime
                )
            self.db_oper.exe_insert(sql, vals)
            comm.PLog.Log("入库成功.")
        except :
            print traceback.format_exc()

a = wechat_get_content()
a.get_url_first()
