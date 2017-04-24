# !/usr/bin/python
# -*- coding: utf-8 -*-
import requests
url = '''https://m.jianke.com/a/20160827'''

a = requests.get(url)
open('a.txt', 'wb').write(a.content)