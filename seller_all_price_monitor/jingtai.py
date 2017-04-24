# !/usr/bin/python
# coding:utf-8

import requests
import urllib
# import chardet


def gethtml(url):
    response = requests.get(url)
    response_body = response.content
    response_body = response_body.decode('GB2312', 'ignore')
    response_body = response_body.encode("utf-8", 'ignore')
    open("aa.txt","ab").write(response_body)
    print response_body

def get_url(url):
    f = urllib.urlopen(url)
    response_body = f.read()
    response_body = response_body.decode('utf8')
    print response_body

url = "http://www.360kad.com/product/4024.shtml"
a = gethtml(url)
# a = get_url(url)