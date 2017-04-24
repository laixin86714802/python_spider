#!/usr/bin/env python
# -*- coding: utf-8 -*-

import MySQLdb
import traceback
import datetime
import time

class AdvertClickDataPrepare(object):
    '''广告点击数据处理'''
    def __init__(self):
        self.db = MySQLdb.connect(
            "172.17.240.5",
            "root",
            "jianke@123",
            "DesignerDB",
            charset="utf8")
        self.cursor = self.db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        self.prov = ['安徽省','澳门特别行政区','北京市','福建省','甘肃省','广东省','广西壮族自治区','贵州省','海南省','河北省',
'河南省','黑龙江省','湖北省','湖南省','吉林省','江苏省','江西省','辽宁省','内蒙古自治区','宁夏回族自治区','青海省','山东省',
'山西省','陕西省','上海市','四川省','台湾省','天津市','西藏自治区','香港特别行政区','新疆维吾尔自治区','云南省','浙江省',
'重庆市','广东省','青海省','新疆维吾尔自治区',]

    def CloseProcess(self):
        '''关闭数据库对象和连接'''
        self.cursor.close()
        self.db.close()

    def getClickDate(self):
        '''获取所有广告id'''
        try:
            # 获取adid
            sql_adid = " SELECT adid FROM `bas_ad_inf` WHERE adid is not null AND adid <> 'NULL' AND ad_company not like '%测试%' GROUP BY adid "
            self.cursor.execute(sql_adid)
            adid_item = self.cursor.fetchall()
            return adid_item
        except:
            print traceback.format_exc()
        # finally:
        #     self.cursor.close()
        #     self.db.close()

    def getRealClickData(self, date, adid):
        '''获取实际点击省份、点击数'''
        try:
            # 获取adid
            sql_adid = ''' SELECT A.adid, B.province, B.click, A.`condition`, B.time
            FROM bas_ad_inf as A, shw_adver_area_click as B
            WHERE A.adid = B.adid AND B.time = '%s' AND A.adid = '%s'
            GROUP BY A.adid, B.province ''' % (date, adid)
            self.cursor.execute(sql_adid)
            adid_item = self.cursor.fetchall()
            # 如果没有数据, 返回0
            if len(adid_item) == 0:
                return 0
            else:
                return adid_item
        except:
            print traceback.format_exc()
        # finally:
        #     self.cursor.close()
        #     self.db.close()

    def getAdvertiesClickData(self, adid):
        '''获取投放省份'''
        try:
            prov_arr = []
            sql_adverties = ''' SELECT A.adid, if(B.click_province is null, '其他', B.click_province) as prov FROM `bas_ad_inf` as A, bas_area_match as B WHERE adid is not null AND adid <> 'NULL' AND A.prov_id = B.prov_id AND ad_company not like '%%测试%%' AND A.adid = '%s' GROUP BY A.adid, A.prov_id ''' % adid
            self.cursor.execute(sql_adverties)
            adverties_item = self.cursor.fetchall()
            # 填补全国投放
            if len(adverties_item) == 1:
                if adverties_item[0]['prov'] == '':
                    adid = adverties_item[0]['adid']
                    for i in self.prov:
                        prov_arr.append({'adid' : adid, 'prov' : i.decode('utf-8')})
                    return prov_arr
            # 非全国投放
            return adverties_item
        except:
            print traceback.format_exc()
        # finally:
        #     self.cursor.close()
        #     self.db.close()

    def DealClickData(self, real_click_data, adverties_click_data):
        '''处理广告数据'''
        adverties_prov = []
        click_prov = []
        # 投放省份
        for adverties_data in adverties_click_data:
            adverties_prov.append(adverties_data['prov'])
        # 点击省份
        for click_data in real_click_data:
            click_prov.append(click_data['province'])
        # 求差集，在投放省份中但不在点击省份中
        ret_prov = list(set(adverties_prov).difference(set(click_prov)))
        # 补全有点击数据
        for real_data in real_click_data:
            if int(real_data['condition']) == 0:
                if real_data['province'] in adverties_prov:
                    # 有投放有点击
                    if real_data['click'] != 0:
                        real_data['state'] = 1
                    # 有投放没点击
                    else:
                        real_data['state'] = 2
                else:
                    # 没投放有点击(点击省份不在投放省份)
                    real_data['state'] = 3
                    real_data['condition'] = None

            # else:
            #     if real_data['province'] in adverties_prov:
            #         # 没投放有点击
            #         if real_data['click'] != 0:
            #             real_data['state'] = 3
            #         # 没投放没点击
            #         pass
            #         # else:
            #         #     real_data['state'] = 4
            #     else:
            #         # 没投放有点击
            #         real_data['state'] = 3

        # 补全差集中数据
        real_click_data = list(real_click_data)
        for i in ret_prov:
            # 有投放没点击
            if real_click_data[0]['condition'] is None:
                condition = 0
            else:
                condition = int(real_click_data[0]['condition'])
            if condition == 0:
                real_click_data.append({'province' : i, 'state' : 2, 'adid' : real_click_data[0]['adid'], 'time' : real_click_data[0]['time'], 'click' : 0, 'condition' : 0})
            # 没投放没点击
            pass
            # else:
            #     real_click_data.append({'province' : i, 'state' : 4, 'adid' : real_click_data[0]['adid'], 'time' : real_click_data[0]['time'], 'click' : 0, 'condition' : real_click_data[0]['condition']})
        return real_click_data

    def load_to_db(self, item):
        '''入库函数'''
        for data in item:
            try:
                if data.has_key('state'):
                    collecttime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(time.time())))
                    sql = '''insert into wrk_adver_deal(province, state, adid, time, click, `condition`) values(%s, %s, %s, %s, %s, %s)'''
                    vals = (
                        data["province"],
                        int(data["state"]),
                        int(data["adid"]),
                        data["time"],
                        int(data["click"]),
                        data["condition"]
                        )
                    self.cursor.execute(sql, vals)
                    print "[", collecttime, "]", u"入库成功."
            except :
                print traceback.format_exc()
            finally:
                self.db.commit()

    def datelist(self, start, end):
        '''生成日期列表'''
        start_date = datetime.date(*start)
        end_date = datetime.date(*end)
        result = []
        curr_date = start_date
        while curr_date != end_date:
            result.append("%04d-%02d-%02d" % (curr_date.year, curr_date.month, curr_date.day))
            curr_date += datetime.timedelta(1)
        result.append("%04d-%02d-%02d" % (curr_date.year, curr_date.month, curr_date.day))
        return result

    def TodayDate(self):
        '''获取当天时间'''
        result = time.strftime('%Y-%m-%d', time.localtime(int(time.time())))
        return result

if __name__ == '__main__':
    try:
        a = AdvertClickDataPrepare()
        adid = a.getClickDate()
        date = a.TodayDate()
        for j in adid:
            real_click_data = a.getRealClickData(date, int(j['adid']))
            # 当前没有数据, 进行下次循环
            if real_click_data == 0:
                continue
            adverties_click_data = a.getAdvertiesClickData(int(j['adid']))
            deal_with_data = a.DealClickData(real_click_data=real_click_data, adverties_click_data=adverties_click_data)
            a.load_to_db(deal_with_data)
    except:
        print traceback.format_exc()
    finally:
        a.CloseProcess()