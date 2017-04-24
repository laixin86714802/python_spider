# !/usr/bin/python
# -*- coding:utf-8 -*-
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME:  wechat_ten_page_sprider.py
# VERSION:   1.0
# CREATED:   2016-12-6 11:19:59
# AUTHOR:    xuexiang
# DESCRIPTION: 
#
# HISTORY: 
#*************************************************************
import os
import re
import time
import requests
import traceback
import conf.db_conf
from ftplib import FTP
import calendar as cal
from comm.db_helper import db_helper_class

class wechat_get_content(object):
    ''' 微信关键字爬虫
        根据数据库中录入的关键字进行搜索
        文章信息入数据库
        文章下载至本地
        原创文章图片下载至FTP服务器
    '''
    def __init__(self):
        # 数据库对象
        self.db_oper = db_helper_class(conf.db_conf)
        # 原创标识
        self.original_word = '''<span\sid="copyright_logo"\sclass="rich_media_meta\smeta_original_tag">原创</span>'''
        # 简介
        self.intro = '''(?:<p\sclass="txt-info".*?>)(?P<intro>.*?)(?:</p>)'''
        # 代理IP
        # self.IP = {"http":"121.14.6.236:80"}
        self.IP = {"http":"218.103.60.205:8080"}
        # 本地图片存储路径
        self.pictrue_uri = "F:\\pictrue_3\\"
        # 服务器图片后缀
        self.pictrue_suffix = "_3.jpg"

    def get_proxies(self):
        '''阿布云代理服务器'''
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
            # "https" : proxyMeta,
        }
        return proxies

    def get_free_proxies(self):
        '''免费获取代理'''
        pass

    def get_url_first(self):
        '''数据库中提取关键词'''
        try:
            item = {}
            # 获取关键词列表
            sql = '''SELECT `channel`, `catId`, `keyword` FROM tb_wechat_table WHERE id > 960 and id <= 1440'''
            (get_num,get_item) = self.db_oper.exe_search(sql)
            # 遍历关键词列表
            for i in xrange(0,get_num):
                # 获取频道、栏目ID、关键词
                item["channel"] = get_item[i]["channel"]
                item["catId"] = get_item[i]["catId"]
                item["keyword"] = get_item[i]["keyword"]
                # 按年月全文搜索文章(时间频率为每个月,类型为图集)
                date_mould = "%d-%s-%s"
                year = [2013, 2014, 2015, 2016]
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
                # 设置代理服务器
                # proxies = self.get_proxies()
                self.get_list_content(item=item, url=url)
        except:
            print traceback.format_exc()

    def get_list_content(self, item, url):
        '''获取列表'''
        try:
            for i in range(1, 11):
                url_list = url + "&page=" + str(i)
                try:
                    keyword_content = requests.get(url_list, proxies=self.get_proxies(), timeout=20)
                except (requests.exceptions.ConnectTimeout, requests.exceptions.Timeout):
                    print u"列表页连接超时"
                if keyword_content:
                    response = keyword_content.content
                    # 频繁访问出现验证码
                    re_visit = "您的访问过于频繁"
                    get_visit = re.findall(re_visit, response, re.S | re.I)
                    if get_visit:
                        print u"验证码出现"
                        # 换IP重新请求
                        response = self.deblocking(url_list, req_type=re_visit)
                    # 等待时间60秒
                    print u"休眠1秒"
                    print u"当前页数:%s" % i
                    time.sleep(1)
                    # 获取该页段落
                    re_detail = '''<div\sclass="txt-box">.*?</span>\s+</div>'''
                    get_detail = re.findall(re_detail, response, re.S | re.I)
                    if get_detail is None:
                        continue
                    # 计数
                    print u"该页个数: %s" % len(get_detail)
                    # 分段解析
                    for deatil_item in get_detail:
                        # 提交至获取详情页
                        self.get_detail_content(item, deatil_item)
                else:
                    return
        except:
            print traceback.format_exc()

    def get_detail_content(self, item, deatil_item):
        '''分析段落'''
        try:
            # 获取url
            re_url = '''(?:<a\starget="_blank"\shref=")(?P<url>.*?)(?:")'''
            get_url = re.search(re_url, deatil_item, re.S | re.I)
            item["url"] = ""
            if get_url:
                print "-----------------------------------"
                print u"关键字:%s" % (item["keyword"])
                detail_url = get_url.group("url")
                detail_url = detail_url.replace('&amp;','&')
                # 永久链接密钥
                # "&pass_ticket=qMx7ntinAtmqhVn+C23mCuwc9ZRyUp20kIusGgbFLi0=&uin=MTc1MDA1NjU1&ascene=1"
                item["url"] = detail_url

            # 获取阅读量
            re_read_num = '''(?:<span\sclass="s1">)(?P<read_num>.*?)(?:</span>)'''
            get_read_num = re.search(re_read_num, deatil_item, re.S | re.I)
            item["read_num"] = ""
            if get_read_num:
                item["read_num"] = get_read_num.group("read_num")

            # 获取发布时间
            re_release_time = '''(?:<div\sclass="s-p"\st=")(?P<release_time>\d+)(?:">)'''
            get_re_release_time = re.search(re_release_time, deatil_item, re.S | re.I)
            item["release_time"] = ""
            if get_re_release_time:
                release_time = int(get_re_release_time.group("release_time"))
                x = time.localtime(release_time)
                item["release_time"] = time.strftime('%Y-%m-%d %H:%M:%S',x)
            # 获取简介
            re_intro = '''(?:<p\sclass="txt-info".*?>)(?P<intro>.*?)(?:</p>)'''
            get_intro = re.search(re_intro, deatil_item, re.S | re.I)
            item["intro"] = ""
            if get_intro:
                item["intro"] = get_intro.group("intro")
                item["intro"] = item["intro"].replace('<em><!--red_beg-->','')
                item["intro"] = item["intro"].replace('<!--red_end--></em>','')
            # 获取公共号名称
            re_source_name = '''(?:data-sourcename=")(?P<source_name>.*?)(?:")'''
            get_sourcename = re.search(re_source_name, deatil_item, re.S | re.I)
            item["source_name"] = ""
            if get_sourcename:
                item["source_name"] = get_sourcename.group("source_name")
            # 获取文章标题
            re_title = '''(?:<a\starget="_blank"\shref=.*?\sid=.*?uigs=".*?>)(?P<title>.*?)(?:</a>)'''
            get_title = re.search(re_title, deatil_item, re.S | re.I)
            item["title"] = ""
            if get_title:
                item["title"] = get_title.group("title")
                # 替换标题中样式
                item["title"] = item["title"].replace('<em><!--red_beg-->','').replace('<!--red_end--></em>','')
                # 标题中替换\/:*?"<>|等非法命名字符
                item["title"] = item["title"].replace("\\", "-").replace("/", "-").replace(":", "：").replace("|", "-").replace(" ", "")
                item["title"] = item["title"].replace("*", "-").replace("?", "？").replace("\"", "'").replace("<", "《").replace(">", "》")
            # 入库查重
            if item["source_name"] != "" and item["title"] != "":
                database_num = self.boolean_repeat(title=item["title"], source_name=item["source_name"])
                if database_num > 0:
                    print u"重复, 进行下次循环"
                    return
            # 获取文章详情
            self.get_detail(item)
        except:
            print traceback.format_exc()

    def get_detail(self, item):
        '''获取详情'''
        try:
            # proxies=self.getRandomIP()
            try:
                resp = requests.get(item["url"], proxies=self.get_proxies(), timeout=20)
            except (requests.exceptions.ConnectTimeout, requests.exceptions.Timeout):
                    print u"详情页连接超时"
            if resp:
                # print "IP:", proxies
                print u"已获取详情"
                detail_html = resp.content
                # 频繁访问出现验证码
                re_visit = '''<div\sstyle="global_error_msg\swarn">'''
                get_visit = re.findall(re_visit, resp.content, re.S | re.I)
                if get_visit:
                    print u"操作过于频繁"
                    # 更换IP继续
                    self.deblocking(item["url"], re_visit)
                    return
                # 获取公共号
                re_source = '''(?:<label\sclass="profile_meta_label">微信号</label>\s+<span\sclass="profile_meta_value">)(?P<source>.*?)(?:</span>)'''
                get_source = re.search(re_source, detail_html, re.S | re.I)
                item["source"] = ""
                if get_source:
                    item["source"] = get_source.group("source")
                # 获取正文
                re_content = '''<div\sclass="rich_media_content.*?</div>'''
                get_content = re.findall(re_content, detail_html, re.S | re.I)
                if get_content:
                    wechat_content = get_content[0]
                    wechat_content = wechat_content.replace('data-src', 'src')
                    # 正文编码
                    wechat_content = wechat_content.decode("utf-8", 'ignore')
                    wechat_content = wechat_content.encode("GB2312", 'ignore')
                    # 原创标识
                    item["original"] = 0
                    original = re.findall(self.original_word, detail_html, re.S | re.I)
                    if original:
                        item["original"] = 1
                    # 验证留言
                    item["message"] = 0
                    message = re.findall('''<a\shref="\#comment">写留言''', detail_html, re.S | re.I)
                    if message:
                        item["message"] = 1
                    # 验证原创并写入文件
                    self.boolean_original(item=item, wechat_content=wechat_content)
                else:
                    print u"无法获取正文"
                    return
            else:
                return
        except:
            print traceback.format_exc()

    def boolean_original(self, item, wechat_content):
        '''验证原创并写入文件'''
        try:
            # keyword编码utf-8, 作为文件夹名
            keyword = item["keyword"]
            title = item["title"]
            source_name = item["source_name"]
            keyword = keyword.encode("GB2312", 'ignore')
            if title:
                title = title.decode("utf-8", 'ignore')
                title = title.encode("GB2312", 'ignore')
            if source_name:
                source_name = source_name.decode("utf-8", 'ignore')
                source_name = source_name.encode("GB2312", 'ignore')
            print u"标题:", title
            if item["original"] == 1 or item["message"] == 1:
                print u"*****获取原创文章*****"
                # 写入文件
                m_outpath = "E:\\wechat_article\\original\\%s\\%s" % (str(item["channel"]), keyword)
                if(not(os.path.exists(m_outpath))):
                    os.mkdir(m_outpath)
                uri = "E:\\wechat_article\\original\\%s\\%s\\%s_%s.html" % (str(item["channel"]), keyword, title, source_name)
                f = open(uri, "wb")
                f.write(wechat_content)
                f.close()
                # 替换文章中图片
                wechat_content = self.replace_picture(wechat_content=wechat_content, uri=uri)
            else:
                print u"非原创文章"
                # 写入文件
                m_outpath = "E:\\wechat_article\\not_original\\%s\\%s" % (str(item["channel"]), keyword)
                if(not(os.path.exists(m_outpath))):
                    os.mkdir(m_outpath)
                uri = "E:\\wechat_article\\not_original\\%s\\%s\\%s_%s.html" % (str(item["channel"]), keyword, title, source_name)
                f = open(uri, "wb")
                f.write(wechat_content)
                f.close()
            # 入库
            self.load_to_db(item)
        except:
            print traceback.format_exc()

    def load_to_db(self, item):
        '''入库函数'''
        try:
            collecttime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(time.time())))
            sql = '''insert into tb_wechat_detail(channel,catId,keyword,read_num,source,source_name,title,intro,original,message,url,release_time,collect_time) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
            vals = (
                item["channel"],
                item["catId"],
                item["keyword"],
                item["read_num"],
                item["source"],
                item["source_name"],
                item["title"],
                item["intro"],
                item["original"],
                item["message"],
                item["url"],
                item["release_time"],
                collecttime
                )
            self.db_oper.exe_insert(sql, vals)
            print "[", collecttime, "]", u"入库成功."
        except :
            print traceback.format_exc()

    def replace_picture(self, wechat_content, uri):
        '''替换文章中的图片'''
        get_picture = re.findall('''src="(.*?)"''', wechat_content, re.S | re.I)
        if get_picture:
            count = 0
            for picture_item in get_picture:
                try:
                    # 验证pirture_item格式
                    a = re.findall('''^http''', picture_item, re.S | re.I)
                    if len(a) == 0:
                        continue
                    # 等待1秒
                    time.sleep(1)
                    count += 1
                    # 请求图片
                    try:
                        picture_var = requests.get(picture_item, proxies=self.get_proxies(), timeout=20)
                    except (requests.exceptions.ConnectTimeout, requests.exceptions.Timeout):
                        print u"请求图片连接超时"
                    if picture_var:
                        picture_value = picture_var.content
                    else:
                        print u'下载图片失败'
                        continue
                    # 获取日期加时间戳
                    date_time = time.strftime('%Y%m%d',time.localtime(time.time()))
                    time_stamp = str(int(time.time()))
                    pictrue_name = date_time + time_stamp + self.pictrue_suffix
                    # 保存至本地
                    pictrue_path = self.pictrue_uri + pictrue_name
                    f_pictrue = open(pictrue_path, "wb")
                    f_pictrue.write(picture_value)
                    f_pictrue.close()
                    # 服务器写入图片文件
                    self.ping_picture_server(pictrue_path=pictrue_path, pictrue_name=pictrue_name)
                    # 新图片链接
                    path = 'http://p.jianke.net/article/201612/%s' % pictrue_name
                    # 替换文章中链接
                    wechat_content = wechat_content.replace(picture_item, path)
                    print u"图片替换成功:",count
                except:
                    print traceback.format_exc()
            f = open(uri, "wb")
            f.write(wechat_content)
            f.close()
                

    def ping_picture_server(self, pictrue_path, pictrue_name):
        '''连接FTP服务器, 并存放图片'''
        try:
            ftp = FTP()
            # 连接FTP服务器
            ftp.connect('118.194.44.47', 4098, 20)
            # 登录
            ftp.login('imgupdate','JK_img@123')
            path = '/article/201612/'
            remotepath = path + pictrue_name
            # 设置FTP图片存储路径
            ftp.cwd(path)
            fp=open(pictrue_path,'rb')
            bufsize = 1024
            #上传文件
            ftp.storbinary('STOR '+ remotepath, fp, bufsize)
            ftp.set_debuglevel(0)
            ftp.quit()  
        except :
            print traceback.format_exc()

    def boolean_repeat(self, title, source_name):
        '''数据库查重函数'''
        try:
            sql = '''SELECT * FROM `tb_wechat_detail` WHERE title="%s" and source_name="%s"''' % (title, source_name)
            (get_num,get_item) = self.db_oper.exe_search(sql)
            return get_num
        except :
            print traceback.format_exc()

    def deblocking(self, url, req_type):
        ''' 换IP重新请求
            最多尝试60次
            如还是无法获取内容则放弃
        '''
        try:
            for i in range(0, 60):
                keyword_content = requests.get(url, proxies=self.get_proxies(), timeout=20)
                if keyword_content:
                    response = keyword_content.content
                    # 频繁访问出现验证码
                    re_visit = req_type
                    get_visit = re.findall(re_visit, response, re.S | re.I)
                    if get_visit:
                        print u"请求内容失败, 更换IP"
                    else:
                        print u"更换IP请求内容成功！"
                        return response
            return
        except:
            print traceback.format_exc()

a = wechat_get_content()
a.get_url_first()