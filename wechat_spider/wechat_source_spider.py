# !/usr/bin/python
# -*- coding: utf-8 -*-

import time
import re
import conf.db_conf
from comm.db_helper import db_helper_class
import traceback
import requests
import os
from ftplib import FTP

class wechat_get_content(object):
    def __init__(self):
        # 本地数据库对象
        self.db_oper = db_helper_class(conf.db_conf)
        # 原创标识
        self.original_word = '''<span\sid="copyright_logo"\sclass="rich_media_meta\smeta_original_tag">原创</span>'''
        # 本地图片存储路径
        self.pictrue_uri = "F:\\pictrue_source\\"
        # 服务器图片后缀
        self.pictrue_suffix = "_sor.jpg"

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
            "https" : proxyMeta,
        }
        return proxies

    def get_url_first(self):
        '''主程序'''
        try:
            # count = 0
            sql = '''SELECT channel, catId, real_source FROM `tb_wechat_source` WHERE real_source != "" and id > 134'''
            (a, b) = self.db_oper.exe_search(sql)
            item = {}
            for source_item in b:
                item["catId"] = source_item["catId"]
                item["channel"] = source_item["channel"]
                item["source_name"] = source_item["real_source"]
                print "--------------------------------------"
                print u"栏目名称:%s" % source_item["channel"]
                url = "http://weixin.sogou.com/weixin?type=1&query=%s&ie=utf8&_sug_=n&_sug_type_=" % source_item["real_source"]
                source_list = requests.get(url, proxies=self.get_proxies(), timeout=20)
                open('a.txt', 'wb').write(source_list.content)
                re_visit = "请输入验证码"
                get_visit = re.findall(re_visit, source_list.content, re.S | re.I)
                if source_list:
                    if get_visit:
                        print u"搜索页验证码出现"
                        # 提交至重新请求
                        self.deblocking(url, re_visit)
                    print u"休眠1秒"
                    time.sleep(1)
                    # 获取url
                    item["source_url"] = ""
                    re_source_url = '''(?:<p\sclass="tit">\s+<a.*?href=")(?P<source_url>.*?)(?:">)'''
                    get_source_url = re.findall(re_source_url, source_list.content, re.S | re.I)
                    if get_source_url:
                        source_url = get_source_url[0]
                        source_url = source_url.replace("&amp;", "&")
                        item["source_url"] = source_url
                        # 传递至列表页
                        self.get_list_content(item)
        except:
            print traceback.print_exc()

    def get_list_content(self, item):
        '''获取该公众号下文章列表'''
        try:
            list_content = requests.get(item["source_url"], proxies=self.get_proxies(), timeout=20)
            if list_content:
                re_visit = "请输入验证码"
                get_visit = re.findall(re_visit, list_content.content, re.S | re.I)
                if get_visit:
                    print u"列表页验证码出现"
                    # 提交至重新请求
                    self.deblocking(item["source_url"], re_visit)
                # 获取文章页url
                re_article = '''"content_url":"(.*?)",'''
                get_article = re.findall(re_article, list_content.content, re.S | re.I)
                if get_article is None:
                    print u"该公众号消息数为空"
                    return
                # 获取简介
                re_intro = '''"digest":"(.*?)",'''
                get_intro = re.findall(re_intro, list_content.content, re.S | re.I)
                # 计数
                print u"消息个数: %s" % len(get_article), len(get_intro)
                item["intro"] = ""
                # 链接传递至详情页
                for i in range(0, len(get_article)):
                    deatil_item = get_article[i].replace("&amp;", "&")
                    item["url"] = "http://mp.weixin.qq.com" + deatil_item
                    item["intro"] = get_intro[i]
                    # 提交至获取详情页
                    self.get_detail_content(item)
        except:
            print traceback.print_exc()

    def get_detail_content(self, item):
        '''获取该文章中详情'''
        try:
            detail_content = requests.get(item["url"], proxies=self.get_proxies(), timeout=20)
            if detail_content:
                # 公共号
                item["source"] = ""
                re_source = '''(?:<label\sclass="profile_meta_label">微信号</label>\s+<span\sclass="profile_meta_value">)(?P<source>.*?)(?:</span>)'''
                get_source = re.search(re_source, detail_content.content, re.S | re.I)
                if get_source:
                    item["source"] = get_source.group("source")
                # 标题
                item["title"] = ""
                re_title = '''(?:<title>)(?P<title>.*?)(?:</title>)'''
                get_title = re.search(re_title, detail_content.content, re.S | re.I)
                if get_title:
                    item["title"] = get_title.group("title")
                    # 标题中替换\/:*?"<>|等非法命名字符
                    item["title"] = item["title"].replace("\\", "-").replace("/", "-").replace(":", "：").replace("|", "-").replace(" ", "")
                    item["title"] = item["title"].replace("*", "-").replace("?", "？").replace("\"", "'").replace("<", "《").replace(">", "》")
                    # 查重
                    database_num = self.boolean_repeat(item["title"])
                    if database_num > 0:
                        print u"重复, 进行下次循环"
                        return
                # 发布时间
                item["release_time"] = ""
                re_date = '''(?:var\sct\s=\s")(?P<date>.*?)(?:";)'''
                get_date = re.search(re_date, detail_content.content, re.S | re.I)
                if get_date:
                    date = time.localtime(int(get_date.group("date")))
                    item["release_time"] = time.strftime('%Y-%m-%d %H:%M:%S',date)
                # 原创标识
                item["original"] = 0
                original = re.findall(self.original_word, detail_content.content, re.S | re.I)
                # 获取正文
                re_content = '''<div\sclass="rich_media_content.*?</div>'''
                get_content = re.findall(re_content, detail_content.content, re.S | re.I)
                if get_content:
                    wechat_content = get_content[0]
                    wechat_content = wechat_content.replace('data-src', 'src')
                    # 正文编码
                    wechat_content = wechat_content.decode("utf-8", 'ignore')
                    wechat_content = wechat_content.encode("GB2312", 'ignore')
                    # 验证原创并写入文件
                    self.boolean_original(item=item, original=original, wechat_content=wechat_content)
        except:
            print traceback.print_exc()

    def boolean_original(self, item, original, wechat_content):
        '''验证原创并写入文件'''
        try:
            # keyword编码utf-8, 作为文件夹名
            title = item["title"]
            source_name = item["source_name"]
            channel = item["channel"]
            if title:
                title = title.decode("utf-8", 'ignore').encode("GB2312", 'ignore')
            if source_name:
                source_name = source_name.encode("GB2312", 'ignore')
            if channel:
                channel = channel.encode("GB2312", 'ignore')
            print "----------------------------"
            print u"标题:", title
            if original:
                print u"*****获取原创文章*****"
                item["original"] = 1
                # 写入文件
                m_outpath = "F:\\wechat_article_source\\original\\%s" % channel
                if(not(os.path.exists(m_outpath))):
                    os.mkdir(m_outpath)
                mm_outpath = "F:\\wechat_article_source\\original\\%s\\%s" % (channel, source_name)
                if(not(os.path.exists(mm_outpath))):
                    os.mkdir(mm_outpath)
                uri = "F:\\wechat_article_source\\original\\%s\\%s\\%s.html" % (channel, source_name, title)
                f = open(uri, "wb")
                f.write(wechat_content)
                f.close()
                # 替换文章中图片
                wechat_content = self.replace_picture(wechat_content=wechat_content, uri=uri)
            else:
                print u"非原创文章"
                # 写入文件
                m_outpath = "F:\\wechat_article_source\\not_original\\%s" % channel
                if(not(os.path.exists(m_outpath))):
                    os.mkdir(m_outpath)
                mm_outpath = "F:\\wechat_article_source\\not_original\\%s\\%s" % (channel, source_name)
                if(not(os.path.exists(mm_outpath))):
                    os.mkdir(mm_outpath)
                uri = "F:\\wechat_article_source\\not_original\\%s\\%s\\%s.html" % (channel, source_name, title)
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
            sql = '''insert into tb_wechat_source_data(`channel`, `catId`, `source`, `source_name`, `title`,`intro`,`original`, `url`, `release_time`, collect_time) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
            vals = (
                item["channel"],
                item["catId"],
                item["source"],
                item["source_name"],
                item["title"],
                item["intro"],
                item["original"],
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

    def boolean_repeat(self, title):
        '''数据库查重函数'''
        try:
            sql = '''SELECT * FROM `tb_wechat_source_data` WHERE title="%s"''' % (title)
            (get_num,get_item) = self.db_oper.exe_search(sql)
            return get_num
        except :
            print traceback.format_exc()

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

a = wechat_get_content()
a.get_url_first()
