# !/usr/bin/python
# -*- coding: utf-8 -*-
import requests
import re
import conf.db_conf
from comm.db_helper import db_helper_class
import time
import os
import traceback
from ftplib import FTP
# 养生堂pc_3----最多14页
# 爱生活pc_6
# 辣妈帮pc_11
# 旅行家pc_13
# 美食家pc_15
class wechat_get_content(object):
    ''' 微信栏目爬虫
        根据提供的栏目名称解析url
        文章信息入数据库
        文章下载至本地
        原创文章图片下载至FTP服务器
    '''
    def __init__(self):
        # 数据库对象
        self.db_oper = db_helper_class(conf.db_conf)
        self.pictrue_suffix = "_pc.jpg"
        self.original_word = '''<span\sid="copyright_logo"\sclass="rich_media_meta\smeta_original_tag">原创</span>'''
        self.pictrue_uri = "F:\\pictrue_pc\\"
    def get_list(self):
        item = {}
        url_list = [
            "http://weixin.sogou.com/pcindex/pc/pc_3/pc_3.html",
            "http://weixin.sogou.com/pcindex/pc/pc_6/pc_6.html",
            "http://weixin.sogou.com/pcindex/pc/pc_11/pc_11.html",
            "http://weixin.sogou.com/pcindex/pc/pc_13/pc_13.html",
            "http://weixin.sogou.com/pcindex/pc/pc_15/pc_15.html",
        ]
        for j in range(0, 5):
            if j == 0:
                item["channel"] = "养生堂"
            elif j ==1:
                item["channel"] = "爱生活"
            elif j ==2:
                item["channel"] = "辣妈帮"
            elif j ==3:
                item["channel"] = "旅行家"
            elif j ==4:
                item["channel"] = "美食家"
            a = requests.get(url_list[j], timeout=10)
            self.get_list_content(a.content, item)
            for i in range(1, 15):
                url = re.sub("\w+.html", str(i)+".html", url_list[j])
                b = requests.get(url, timeout=10)
                self.get_list_content(b.content, item)

    def get_list_content(self, content, item):
        # 分块
        detail_list = re.findall("<li\sd=.*?</div>\s+</div>", content, re.S | re.I)
        if detail_list:
            for detail_item in detail_list:
                # 获取标题
                re_title = re.search("(?:<h3><a.*?>)(?P<title>.*?)(?:</a></h3>)", detail_item, re.S | re.I)
                item["title"] = ""
                if re_title:
                    get_title = re_title.group("title")
                    item["title"] = get_title
                    # 标题中替换\/:*?"<>|等非法命名字符
                    item["title"] = item["title"].replace("\\", "-").replace("/", "-").replace(":", "：").replace("|", "-").replace(" ", "")
                    item["title"] = item["title"].replace("*", "-").replace("?", "？").replace("\"", "'").replace("<", "《").replace(">", "》")
                # 获取简介
                re_intro = re.search('''(?:<p\sclass="txt-info"\starget="_blank">)(?P<intro>.*?)(?:</p>)''', detail_item, re.S | re.I)
                item["intro"] = ""
                if re_intro:
                    get_intro = re_intro.group("intro")
                    item["intro"] = get_intro
                # 获取url
                re_url = re.search('''(?:<a\suigs=.*?title"\shref=")(?P<url>.*?)(?:")''', detail_item, re.S | re.I)
                item["url"] = ""
                if re_intro:
                    get_url = re_url.group("url")
                    item["url"] = get_url + "&pass_ticket=qMx7ntinAtmqhVn+C23mCuwc9ZRyUp20kIusGgbFLi0=&uin=MTc1MDA1NjU1&ascene=1"
                # 获取阅读量
                re_read_num = re.search('''(?:<span\sclass="s1">)(?P<read_num>.*?)(?:</span>)''', detail_item, re.S | re.I)
                item["read_num"] = ""
                if re_read_num:
                    get_read_num = re_read_num.group("read_num")
                    item["read_num"] = get_read_num
                # 获取公共号名称
                re_source_name = re.search('''(?:data-sourcename=")(?P<source_name>.*?)(?:")''', detail_item, re.S | re.I)
                item["source_name"] = ""
                if re_source_name:
                    get_source_name = re_source_name.group("source_name")
                    item["source_name"] = get_source_name
                # 获取发布时间
                re_release_time = re.search('''(?:<span\sclass="s2"\st=")(?P<release_time>.*?)(?:")''', detail_item, re.S | re.I)
                item["release_time"] = ""
                if re_release_time:
                    release_time = int(re_release_time.group("release_time"))
                    x = time.localtime(release_time)
                    item["release_time"] = time.strftime('%Y-%m-%d %H:%M:%S',x)
                # 入库查重
                database_num = self.boolean_repeat(title=item["title"], source_name=item["source_name"])
                if database_num > 0:
                    print u"重复, 进行下次循环"
                    return
                # 获取详情
                self.get_detail(item)

    def boolean_repeat(self, title, source_name):
        '''数据库查重函数'''
        try:
            sql = '''SELECT * FROM `tb_wechat_channel` WHERE title="%s" and source_name="%s"''' % (title, source_name)
            (get_num,get_item) = self.db_oper.exe_search(sql)
            return get_num
        except :
            print traceback.format_exc()

    def get_detail(self, item):
        '''获取详情'''
        try:
            try:
                resp = requests.get(item["url"], timeout=20)
            except (requests.exceptions.ConnectTimeout, requests.exceptions.Timeout):
                    print u"详情页连接超时"
            if resp:
                # print "IP:", proxies
                print "-----------------------------"
                print u"已获取详情"
                detail_html = resp.content
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
                    wechat_content = wechat_content.replace('data-src','src')
                    # 正文编码
                    wechat_content = wechat_content.decode("utf-8", 'ignore')
                    wechat_content = wechat_content.encode("GB2312", 'ignore')
                    # 原创标识
                    item["original"] = 0
                    original = re.findall(self.original_word, detail_html, re.S | re.I)
                    # 验证原创并写入文件
                    self.boolean_original(item=item, original=original, wechat_content=wechat_content)
                else:
                    print u"无法获取正文"
                    return
            else:
                return
        except:
            print traceback.format_exc()

    def boolean_original(self, item, original, wechat_content):
        '''验证原创并写入文件'''
        try:
            # keyword编码utf-8, 作为文件夹名
            title = item["title"]
            source_name = item["source_name"]
            channel = item["channel"]
            if channel:
                channel = channel.decode("utf-8", 'ignore')
                channel = channel.encode("GB2312", 'ignore')
            if title:
                title = title.decode("utf-8", 'ignore')
                title = title.encode("GB2312", 'ignore')
            if source_name:
                source_name = source_name.decode("utf-8", 'ignore')
                source_name = source_name.encode("GB2312", 'ignore')
            print u"标题:", title
            if original:
                print u"*****获取原创文章*****"
                item["original"] = 1
                # 写入文件
                m_outpath_channel = "F:\\wechat_article\\original\\%s" % channel
                if(not(os.path.exists(m_outpath_channel))):
                    os.mkdir(m_outpath_channel)
                uri = "F:\\wechat_article\\original\\%s\\%s_%s.html" % (channel, title, source_name)
                f = open(uri, "wb")
                f.write(wechat_content)
                f.close()
                # 替换文章中图片
                wechat_content = self.replace_picture(wechat_content=wechat_content, uri=uri)
            else:
                print u"非原创文章"
                # 写入文件
                m_outpath_channel = "F:\\wechat_article\\not_original\\%s" % channel
                if(not(os.path.exists(m_outpath_channel))):
                    os.mkdir(m_outpath_channel)
                uri = "F:\\wechat_article\\not_original\\%s\\%s_%s.html" % (channel, title, source_name)
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
            sql = '''insert into tb_wechat_channel(`channel`, `read_num`, `source`, `source_name`, `title`,`intro`,`original`, `url`, `release_time`, collect_time) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
            vals = (
                item["channel"],
                item["read_num"],
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
                        picture_var = requests.get(picture_item, timeout=20)
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

a = wechat_get_content()
a.get_list()