
#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 taobao_test.py
# VERSION: 	 1.0
# CREATED: 	 2016-05-30 10:14
# AUTHOR: 	 xuexiang
# DESCRIPTION:
#
# HISTORY:
#*************************************************************
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import comm
import re
import comm.PLog
import comm.requests_pkg
import comm.stone_funs
import json

#ip = "36.188.19.157"
ip = "223.104.255.231"
ip = "223.104.171.69"
ip = "113.210.187.106"
ip = "121.8.124.2"
url = 'http://ip.taobao.com/service/getIpInfo.php?ip=' + ip
(http_ok, resp) = comm.requests_pkg.get(url)

return_info = ""

if http_ok:
    #resp_content = comm.stone_funs.ToUtf8(resp.content)

    #resp_content = resp.content.encode('utf-8', 'ignore')
    json_data = json.loads(resp.content)
    
    #country
    contry_name = json_data[u'data'][u'country'].encode('utf-8')
    comm.PLog.Log(contry_name)

    #area
    area_name = json_data[u'data'][u'area'].encode('utf-8')
    comm.PLog.Log(area_name)

    #city
    city_name = json_data[u'data'][u'city'].encode('utf-8')
    comm.PLog.Log(city_name)

    #region
    region_name = json_data[u'data'][u'region'].encode('utf-8')
    comm.PLog.Log(region_name)

    #county
    county_name = json_data[u'data'][u'county'].encode('utf-8')
    comm.PLog.Log(county_name)

    result = []
    result.append(json_data[u'data'][u'ip'].encode('utf-8'))            
    result.append(json_data[u'data'][u'country'].encode('utf-8'))
    result.append(json_data[u'data'][u'country_id'].encode('utf-8'))
    result.append(json_data[u'data'][u'area'].encode('utf-8'))
    result.append(json_data[u'data'][u'area_id'].encode('utf-8'))
    result.append(json_data[u'data'][u'region'].encode('utf-8'))
    result.append(json_data[u'data'][u'region_id'].encode('utf-8'))
    result.append(json_data[u'data'][u'city'].encode('utf-8'))
    result.append(json_data[u'data'][u'city_id'].encode('utf-8'))
    result.append(json_data[u'data'][u'county'].encode('utf-8'))
    result.append(json_data[u'data'][u'county_id'].encode('utf-8'))
    result.append(json_data[u'data'][u'isp'].encode('utf-8'))
    result.append(json_data[u'data'][u'isp_id'].encode('utf-8'))   
    tt= " ".join(result)
    comm.PLog.Log(tt)


    #resp_content = resp.content.decode('utf-8');
    #resp_content = resp_content.strip()
    #comm.PLog.Log("resp_content: " + resp_content)

    #addr_list = re.split(r'\s+', resp_content)
    #comm.PLog.Log(resp_content)

