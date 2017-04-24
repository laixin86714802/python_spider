# !/usr/bin/python
# -*- coding: utf-8 -*-

# import MySQLdb
# import MySQLdb.cursors

# from twisted.enterprise import adbapi             #导入twisted的包
import MySQLdb
import MySQLdb.cursors
import traceback

import re
import requests
import time
# from tmall_all_list.conf.db_conf

# db_host = "172.17.240.6"
# db_user = "root"
# db_passwd = "2016abc"
# db_name = "big_data_platform"

db_host = "172.17.240.5"
db_user = "root"
db_passwd = "jianke@123"
db_name = "test"


class shujuku:
    def __init__(self):
        self.db = MySQLdb.connect(
            db_host,
            db_user,
            db_passwd,
            db_name,
            charset="utf8")
        self.cursor = self.db.cursor(cursorclass=MySQLdb.cursors.DictCursor)

    def __del__(self):
        self.db.commit()
        self.db.close()

    # # 查询函数
    def exe_search(self, sql):
        # 受影响的行数
        a = self.cursor.execute(sql)
        b = self.cursor.fetchall()
        return (a, b)

    # 插入函数
    def exe_insert(self, sql, vals):
        self.cursor.execute(sql, vals)
        self.db.commit()

    # 修改函数
    def exe_update(self, sql):
        self.cursor.execute(sql)
        self.db.commit()

    def do_task(self):

        IP = {'https': 'http://H1F46KFI5PG8TGDD:51AABFBCFCB6B729@proxy.abuyun.com:9010'}
        try:
            # count = 0
            sql = '''SELECT source_name, IFNULL(source,source_name) as source FROM `tb_wechat_source` where url=""'''
            (a, b) = self.exe_search(sql)
            source_item = {}
            for item in b:
                source = item["source"]
                # source_name
                source_item["source_name"] = item["source_name"]
                source_item["source_name"] = source_item["source_name"].encode("utf-8")
                url = "http://weixin.sogou.com/weixin?type=1&query=%s&ie=utf8" % source
                source_list = requests.get(url, timeout=10, proxies=IP)
                re_visit = "您的访问过于频繁"
                get_visit = re.findall(re_visit, source_list.content, re.S | re.I)
                if get_visit:
                    print u"验证码出现"
                    return
                # time.sleep(10)
                # print u"休眠10秒"
                if source_list:
                    open("a.txt", "wb").write(source_list.content)
                    # 获取url
                    source_item["source_url"] = ""
                    re_source_url = '''(?:<p\sclass="tit">\s+<a.*?href=")(?P<source_url>.*?)(?:">)'''
                    get_source_url = re.findall(re_source_url, source_list.content, re.S | re.I)
                    if get_source_url:
                        source_url = get_source_url[0]
                        source_url = source_url.replace("&amp;", "&")
                        source_item["source_url"] = source_url
                    # 获取公众号名称
                    source_item["real_source"] = ""
                    re_real_source = '''(?:<p\sclass="tit">\s+<a.*?">)(?P<source_name>.*?)(?:</a>)'''
                    get_real_source = re.findall(re_real_source, source_list.content, re.S | re.I)
                    if get_real_source:
                        real_source = get_real_source[0].replace("<em><!--red_beg-->", "").replace("<!--red_end--></em>", "")
                        source_item["real_source"] = real_source
                    self.load_to_db(source_item)
        except:
            traceback.print_exc()
    def load_to_db(self, source_item):
        try:
            sql = '''UPDATE `tb_wechat_source` SET url="%s", real_source="%s" WHERE source_name="%s"''' % (source_item["source_url"], source_item["real_source"], source_item["source_name"])
            a = self.exe_update(sql)
            print a
        except:
            traceback.print_exc()


qq = shujuku()
a = qq.do_task()
