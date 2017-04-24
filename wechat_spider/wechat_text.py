# !/usr/bin/python
# -*- coding: utf-8 -*-
# import calendar as cal
# date_mould = "%d-%s-%s"
# year = [2014]
# for every_year in year:
#     for m in range(1, 10):
#         d = cal.monthrange(every_year, m)
#         if m <10:
#             month = "0" + str(m)
#         else:
#             month = str(m)
#         start_month = date_mould % (every_year, month, "01")
#         end_month = date_mould % (every_year, month, d[1])
#         url = "http://weixin.sogou.com/weixin?type=2&ie=utf8&query=%s&tsn=5&ft=%s&et=%s&interation=458754&wxid=&usip=null&from=tool" % ("cctv", start_month, end_month)
#         print url
import requests
import re
a = requests.get("http://mp.weixin.qq.com/s?timestamp=1481876204&src=3&ver=1&signature=3kCm1-dZKd4Okw*38OpZJTNW-CY-7yICXblCcFmFGOpMFX6csBBc3BTYj3cfZMJbB2tRcoBandfB-Dv*0t6tudLtDWdakmha*LW9H3xDwNsoiKx*zx3aRenKVN7qnugrftSmLFPRtxKUIHjpiHDgXauIyjTCyMRopla5Q1kUwhw=", proxies={'http': 'http://H1F46KFI5PG8TGDD:51AABFBCFCB6B729@proxy.abuyun.com:9010'})
b = re.findall('''<a\shref="\#comment">写留言''', a.content, re.S | re.I)
print b
open("a.txt", "wb").write(a.content)
# sql = '''SELECT `channel`, `catId`, `keyword` FROM tb_wechat_table WHERE id <= 480'''
# sql = '''SELECT `channel`, `catId`, `keyword` FROM tb_wechat_table WHERE id > 480 and id <= 960'''
# sql = '''SELECT `channel`, `catId`, `keyword` FROM tb_wechat_table WHERE id > 960 and id <= 1440'''
# sql = '''SELECT `channel`, `catId`, `keyword` FROM tb_wechat_table WHERE id > 1440 and id <= 1920'''
# sql = '''SELECT `channel`, `catId`, `keyword` FROM tb_wechat_table WHERE id > 1920'''