# !/usr/bin/python
# -*- coding:utf-8 -*-
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME:  wechat_interface_CRM.py
# VERSION:   1.0
# CREATED:   2016-12-14 09:50:00
# AUTHOR:    xuexiang
# DESCRIPTION: 
#
# HISTORY: 
#*************************************************************
import time
import requests
import traceback
import conf.db_conf
from comm.db_helper import db_helper_class


class wechat_interface(object):
    """ 将数据库中数据提交至CRM提供接口
        接口格式如下
        http://t-weixin.jianke.com/app/article/AddFromWeiXinArticle
        http://askapi.jianke.com/app/article/AddFromWeiXinArticle
        POST请求, 字符串都要进行URL编码
        参数1(title):表示文章标题
        参数2(catId):表示栏目Id
        参数3(intro):表示简介
        参数4(source):表示文章出处
        参数5(keyword):关键词
        参数6(content):主文内容
    """
    def __init__(self):
        # 接口
        self.interface = "http://askapi.jianke.com/app/article/AddFromWeiXinArticle"
        # 数据库对象
        self.db_oper = db_helper_class(conf.db_conf)
        # 偏移值
        self.offset = 0

    def get_db_data(self):
        '''获取数据库中文章信息'''
        try:
            while True:
                sql = "SELECT id, channel, title, catId, intro, keyword, source_name FROM `tb_wechat_detail` WHERE original=1 and id > 158498 limit 100 OFFSET %s" % self.offset
                self.offset += 100
                (get_num, get_item) = self.db_oper.exe_search(sql)
                if get_num == 0:
                    return
                item = {}
                count = 0
                for article_item in get_item:
                    keyword = article_item["keyword"].encode("GB2312", 'ignore')
                    title = article_item["title"].encode("GB2312", 'ignore')
                    if title == "":
                        continue
                    source_name = article_item["source_name"].encode("GB2312", 'ignore')
                    # 读取文件content
                    # path = "E:\\wechat_article\\original\\%s\\%s\\%s.html" % (str(article_item["channel"]), keyword, title)
                    path = "E:\\wechat_article\\original\\%s\\%s\\%s_%s.html" % (str(article_item["channel"]), keyword, title, source_name)
                    content = open(path, "rb").read()
                    content = content.decode("GB2312").encode("utf-8")
                    # 文件存入字典
                    article_item["content"] = content
                    item["id"] = article_item["id"]
                    item["title"] = article_item["title"].encode("utf-8")
                    item["catId"] = article_item["catId"]
                    item["intro"] = article_item["intro"].encode("utf-8")
                    item["source_name"] = article_item["source_name"].encode("utf-8")
                    item["keyword"] = article_item["keyword"].encode("utf-8")
                    item["content"] = content
                    # 发送post请求
                    self.send_post_requests(item=item)
                    count += 1
                    print u"已传输文章:",count
        except:
            print traceback.format_exc()
    def send_post_requests(self, item):
        '''获取接口，发送post请求'''
        try:
            collecttime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(time.time())))
            params = {
            "title":item["title"],
            "catId":item["catId"],
            "intro":item["intro"],
            "source":item["source_name"],
            "keyword":item["keyword"],
            "content":item["content"],
            }
            feedback = requests.post(self.interface, data=params)
            # 日志
            open("interface.log", "ab").write("["+collecttime+"]  "+feedback.content+"  id="+str(item["id"])+"\n")
        except:
            print traceback.format_exc()


a = wechat_interface()
a.get_db_data()