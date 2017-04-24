#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 random_useragent.py
# VERSION: 	 1.0
# CREATED: 	 2016-01-11 12:38
# AUTHOR: 	 xuexiang
# DESCRIPTION:
#
# HISTORY:
#*************************************************************
import random

user_agent_list = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
    "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
]

cookie_list = {"0":
        {"SUV":"00175E2BDA6B097D57CBCDBE7DA71981",
        "IPLOC":"CN4401",
        "CXID":"860E089DD32C47EE1ECF55ED807B8483",
        "weixinIndexVisited":"1",
        "Hm_lvt_96d9d92b8a4aac83bc206b6c9fb2844a":"1474170419,1474181444",
        "pgv_pvi":"5441667072",
        "m":"3B3BF1EE5348A83F1126D107D0679A9B",
        "GOTO":"Af99046",
        "ld":"3kllllllll2gc8WVQx31FOkc9KdY9rSnLu7JKyllll9lllllpylll5@@@@@@@@@@",
        "ad":"IZllllllll2g8FjPlllllVkcVMklllllLu7JKyllllklllllpqxlw@@@@@@@@@@@",
        "SUID":"7D096BDA3320910A0000000057CD2EFF",
        "YYID":"3B3BF1EE5348A83F1126D107D0679A9B",
        "ABTEST":"6|1480328071|v1",
        "SNUID":"176301B06A6F2830D6BC3C936AE5FEE5",
        "ppinf":"5|1480329006|1481538606|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZTo0NTolRTYlQTElOTElRTQlQkIlQTMlRTUlODUlOEIlRTclOUElODQlRTclOEMlQUJ8Y3J0OjEwOjE0ODAzMjkwMDZ8cmVmbmljazo0NTolRTYlQTElOTElRTQlQkIlQTMlRTUlODUlOEIlRTclOUElODQlRTclOEMlQUJ8dXNlcmlkOjQ0OjBGRUY3RjYyNURFRURDNENENTQ1QTQzRUVGM0NGN0I1QHFxLnNvaHUuY29tfA",
        "pprdig":"P2pI_Pg9yrgKMa_77mxL6oPkwz00TkxpCsDOgjCcAeooqV8sJ_HupoQ2PEcJWFhyRtWeHggUHdu1Utl-76Yn0kpZoMhU7NVPlVVWYyYcPjEr2AfVZtCxkSjMaR7HFfq6_EPOoj2Q5hFLG-KWDjrStcCu2dgQeFtuoDDnoeycu9Y",
        "JSESSIONID":"aaaJAisLxciYQdPWTdxIv",
        "sct":"26",
        "usid":"NNV9tIXWQrAUgBuz",},
        "1":
        {"CXID":"AF57AF81F11CB52EC7BB8426B122709F",
        "SUID":"027C08796773860A5780A0D40005864C",
        "SUV":"1474961333667375",
        "SMYUV":"1477467190974117","ld":"62dpFkllll2Y9VhGlllllVktynUlllllLu7JKyllllYlllllxllll5@@@@@@@@@@",
        "LSTMV":"559%2C616",
        "LCLKINT":"8245",
        "ABTEST":"2|1480474923|v1",
        "weixinIndexVisited":"1",
        "ppinf":"5|1480474972|1481684572|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZToxODolRTYlOTglOUYlRTYlODglQjB8Y3J0OjEwOjE0ODA0NzQ5NzJ8cmVmbmljazoxODolRTYlOTglOUYlRTYlODglQjB8dXNlcmlkOjQ0Ojc5RDFFODAzQjcxRUE2MTkxMTdERjRERDgzM0MzMzlDQHFxLnNvaHUuY29tfA",
        "pprdig":"ZAeDwf32d2mdLSrC3TKobPupkRgdCBKW7MN-tjX8XVFSfJhIJPlq-q3qaA_ZHS6ONxpbajRRsqSTxm-y2RdKa2cnH_XwuNq4yW1jnQkuebnaEXj3sbm20RkDpwZ8N4LCj8Ll1sW3THbF0XikcL9p1gIc_8ITW1_cB6Mblkds11Q",
        "IPLOC":"CN4401",
        "sct":"10","SNUID":"631775C41E185F65EE47B3021E06F9EB",
        "JSESSIONID":"aaahhH07ZiWfx-DoM9UIv",},
        "2":
        {"SUV":"1477387042567550",
        "ld":"UngGykllll2Yp9OjlllllVkYvUwlllllLu7JKyllll9llllllylll5@@@@@@@@@@",
        "CXID":"E30E4186ECFB517F1DD9FA934D27C227",
        "ad":"1yllllllll2YnTr@lllllVkdPgtlllllNxwQMlllll9lllll4qxlw@@@@@@@@@@@",
        "SUID":"7D096BDA3320910A00000000580F2322",
        "ABTEST":"5|1480471144|v1",
        "weixinIndexVisited":"1",
        "sct":"2",
        "SNUID":"5E0B0F681D185F6710FEFD181DA6EE89",
        "JSESSIONID":"aaaKE1wzOYXuk4d2k8UIv",
        "IPLOC":"CN4419",
        "ppinf":"5|1480476228|1481685828|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZToxODolRTUlOUMlOUYlRTglQjElODZ8Y3J0OjEwOjE0ODA0NzYyMjh8cmVmbmljazoxODolRTUlOUMlOUYlRTglQjElODZ8dXNlcmlkOjQ0OkY3ODM2QTZDRUE3MDBENUJGNjA0Q0UyQzQ0Rjg3MDRDQHFxLnNvaHUuY29tfA",
        "pprdig":"jz1247_hIm5-HKTWpCHYrH6pO-sQio2wlzhWuy1R5KUd4lLEI6erKyi2cahws0ZiJY1quOjfAFP66a_Q7G8dSST-KTHM9zBwFGFnEHdQGg-BNB_Uj8cYtjY10-1fNUoVJvXRzJr-GrRB712XmvgLxKjKe7PLGYBUOc0wd_0lP1U",}
}

IP_list = [
    '121.14.6.236:80',
    '218.76.106.78:3128',
    '124.88.67.81:81',
    '124.88.67.19:83',
    '124.88.67.17:843',
-----------------------------
    '113.18.193.9:8080',
    '113.18.193.12:8080',
    '123.233.153.151:8118',
    '91.217.34.137:8080',
    '111.13.7.42:81',
    '27.192.170.83:8118',
    '113.18.193.21:8080',
    '175.162.180.28:8888',
    '113.18.193.23:8080',
    '27.184.131.97:8888',
    '124.88.67.81:843',
    '176.31.96.198:8080',
    '80.1.116.80:80',
    '124.88.67.18:82',
    '218.103.60.205:8080',
    '124.88.67.14:83',
    '113.18.193.11:80',
    # '199.116.113.206:8080',
    '112.124.47.21:8008',
    '27.210.245.44:8888',
    '124.88.67.19:80',
    '124.88.67.83:82',
    '142.4.200.192:80',
    '193.171.90.2:8080',
    '218.25.13.23:80',
    '113.18.193.3:8080',
    '113.18.193.15:8080',
    '197.97.146.62:8080',
    '124.88.67.31:843',
    '113.18.193.7:8080',
]

def getRandomUA():
    ua = random.choice(user_agent_list)
    headers = {"User-Agent": ua} 
    return headers

    
def getRandomCookie():
    cookie_number = str(random.randint(0, 2))
    cookie = cookie_list[cookie_number]
    return cookie

def getRandomIP():
    IP = random.choice(IP_list)
    IP = {'http' : IP}
    return IP
    