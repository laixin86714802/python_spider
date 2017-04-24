import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import spynner
import re
import time
import comm.random_useragent
import MySQLdb
import conf.db_conf
import comm.job_report
import conf.app_conf
import conf.class_conf
import comm.db_helper
import comm.JobSta
import comm.PLog
from comm.comm_processor import CommProcessor


class tmall_list_spider_class():

    def __init__(self):
        comm.PLog.Log("运行实例：天猫处方药列表")
        agent = comm.random_useragent.getRandomUAItem()
        self.browser = spynner.Browser(user_agent=agent)
        # 设置代理
        # browser.set_proxy('http://219.133.31.120:8888')
        self.browser.hide()
        self.db_oper = comm.db_helper.db_helper_class(conf.db_conf)
        # 真实得到的目标链接数量
        self.target_link_cnt = 0

    def down_page(self, url, count, job_id):
        payload_puredata = r'''(?:<div\sid="J_Combo"\sclass="combo">)(?P<sReserve>.*?)(?:<!--start\sPCSceneVideo\s-->)'''
        payload_record_block = r'''(?:<div\sclass="product\s+.*?旗舰店)'''
        try:
            self.browser.load(url=url, load_timeout=120, tries=3)
        except spynner.SpynnerTimeout:
            print 'Timeout.'
        else:
            html = self.browser.html.encode("utf-8")
            html = str(html)
            re_pure_data = re.search(payload_puredata, html, re.S | re.I)
        if re_pure_data is None:
            comm.PLog.Log(
                "[WARNING] 承载页%s, payload_puredata匹配不到! 重新请求:%s" %
                (url, url))
            self.down_page(url, count, job_id)
        else:
            re_pure_data = re_pure_data.group('sReserve')
            comm.PLog.Log(
                "承载页%s, payload_puredata去噪匹配成功." % url)
            reobj = re.compile(payload_record_block, re.S | re.I)
            lstRef = reobj.findall(re_pure_data)
            if lstRef is None:
                comm.PLog.Log(
                    "[WARNING] 承载页%s, payload_record_block匹配失败!" % url)
            currentid = 0

            for record in lstRef:
                currentid = currentid + 1
                # comm.PLog.Log(
                #"承载页%s, payload_record_block匹配成功." %url)
                comm.PLog.Log(
                    "当前进度:%d/%d" %
                    (currentid, count))
                item = {}
                brand_state = 0
                if self.class_id == conf.class_conf.cls_tmfcy_jk:
                    re_brand = r'''(?:<a\sclass="productShop-name.*?class="H">)([^<]+)(?:.*?"H">)([^<]+)(?:.*?class="H">)([^<])(?:.*?class="H">)([^<]+)'''
                    brand = re.search(re_brand, record, re.S)
                    if brand:
                        str_brand = brand.group(1) + brand.group(2)
                        if str_brand == '健客':
                            brand_state = 1
                else:
                    re_brand = r'''(?:<a\sclass="productShop-name.*?class="H">)([^<]+)(?:.*?"H">)([^<]+)(?:.*?class="H">)([^<]+)'''
                    brand = re.search(re_brand, record, re.S)
                    if brand:
                        str_brand = brand.group(1) + brand.group(2) + brand.group(3)
                        if str_brand == '康爱多大药房':
                            brand_state = 1
                re_id = r'''data-id="(.*?)"'''
                re_url = r'''<a\shref="(.*?)"\sclass'''
                re_price = r'''<em\stitle="([\d\.]+?)">'''
                re_name = r'''<a href=(.*?)title="(.*?)" data-p="(.*?)">'''
                re_name1 = r'''title="(.*)'''
                if self.class_id == 800003:
                    item["fld_company"] = '健客大药房旗舰店处方药'
                else:
                    item["fld_company"] = '康爱多大药房旗舰店处方药'
                item["fld_url"] = re.search(re_url, record, re.S).group(1)
                item["fld_url"] = re.sub("//detail.tmall.com",
                                         "https://detail.yao.95095.com", str(item["fld_url"]))
                #item["fld_url"] = "https:" + str(item["fld_url"])
                item["fld_price"] = re.search(re_price, record, re.S)
                if item["fld_price"]:
                    item["fld_price"] = str(item["fld_price"].group(1))
                else:
                    item["fld_price"] = ""
                item["fld_caption"] = re.search(re_name, record, re.S).group(2)
                item["fld_caption"] = re.search(
                    re_name1, item["fld_caption"]).group(1)
                item["fld_remark"] = "%d:%d" % (currentid, count + 1)
                re_productid = re.search(re_id, record, re.S)
                if re_productid:
                    item["fld_productid"] = str(re_productid.group(1))
                else:
                    item["fld_productid"] = ""

                fld_carryinfo = item["fld_caption"]
                if fld_carryinfo is None:
                    comm.PLog.Log(
                        "[WARNING] 承载页%s, payload_record_info匹配失败!" % url)
                # 获取产品Id

                fld_inserttime = time.strftime(
                    '%Y-%m-%d %H:%M:%S', time.localtime(int(time.time())))
                sql = "insert into wrk_tmall_fcy_goods_list(sJobId, sSource, sProductId, sTargetUrl, sCarryingInfo, sState, sPageId, sCollectTime, sRemark) values(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                vals = (
                    job_id,
                    item["fld_company"],
                    item["fld_productid"],
                    item["fld_url"],
                    fld_carryinfo,
                    "No",
                    count + 1,
                    fld_inserttime,
                    item["fld_remark"])
                if brand_state == 1:
                    self.db_oper.exe_insert(sql, vals)
                else:
                    comm.PLog.Log("[WARNING] 匹配到错误官网的产品，url %s" % url)
            self.job_stat.down_ok_count += 1
            comm.PLog.Log("此页获取到%d个商品链接" % currentid)
            self.target_link_cnt += currentid

    def do_task(self, company):
        if company == 'jk':
            self.app_id = conf.app_conf.app_tmfcy_listupdate_id
            self.class_id = conf.class_conf.cls_tmfcy_jk
        else:
            self.app_id = conf.app_conf.app_tmfcy_listupdate_id
            self.class_id = conf.class_conf.cls_tmfcy_kad
        self.job_stat = comm.JobSta.JobSta()
        self.job_id = "%s_%s_%s" % (time.strftime(
            'T%Y%m%d%H%M'), self.app_id, self.class_id)
        comm.PLog.Log("新建任务Id: %s" % self.job_id)
        payload_pagecount = r'''(?:<b\sclass="ui-page-s-len">\d/)(?P<sPageCount>\d+)(?:</b>)'''
        try:
            if company == 'jk':
                # https://list.tmall.com/search_product.htm?cat=55114018&q=健客大药房
                self.browser.load(
                    url=u'https://list.tmall.com/search_product.htm?spm=a220m.1000858.1000721.1.M3hMM6&cat=55114018&q=健客大药房&sort=s&style=g&from=sn_1_cat-qp&tmhkmain=0',
                    load_timeout=120,
                    tries=3)
            else:
                self.browser.load(
                    url=u'https://list.tmall.com/search_product.htm?spm=a220m.1000858.1000721.1.M3hMM6&cat=55114018&q=康爱多大药房&sort=s&style=g&from=sn_1_cat-qp&tmhkmain=0',
                    load_timeout=120,
                    tries=3)
        except spynner.SpynnerTimeout:
            print 'Timeout.'
        else:
            html = self.browser.html
            pagecount = int(re.search(payload_pagecount, html, re.S).group('sPageCount'))
        if pagecount is None:
            comm.PLog.Log("[WARNING] 页数匹配不到! 重新请求")
            self.do_task(self, company)
        else:
            self.job_stat.all_task_count = pagecount
            comm.PLog.Log("初始化job report.")
            comm.job_report.report_start(
                self.app_id, self.class_id, self.job_id,
                self.job_stat.all_task_count, self.db_oper)
            for x in range(0, pagecount):
                comm.PLog.Log("当前真实pageid: %d" % (x + 1))
                if company == 'jk':
                    self.down_page(
                        u'https://list.tmall.com/search_product.htm?spm=a220m.1000858.1000724.10.T7j5PL&cat=55114018&s=%d&q=健客大药房&sort=p&style=g&from=sn_1_cat-qp&industryCatId=55114018&tmhkmain=0&type=pc#J_Filter' %
                        (x * 60), x, self.job_id)
                else:
                    self.down_page(
                        u'https://list.tmall.com/search_product.htm?spm=a220m.1000858.1000724.10.BDUNTq&cat=55114018&s=%d&q=康爱多大药房&sort=p&style=g&from=sn_1_cat-qp&industryCatId=55114018&tmhkmain=0&type=pc#J_Filter' %
                        (x * 60), x, self.job_id)

            if (self.target_link_cnt > 3000):
                comm.PLog.Log("列表页全量下载完成, 更新任务%s状态为complated!" % self.job_id)
                if company == 'jk':
                    sRemark = "jk-fcy"
                else: 
                    sRemark = "kad-fcy"
                comm.job_report.report_finish(
                    self.job_id, self.job_stat, self.db_oper, sRemark)
            else:
                comm.PLog.Log("没有采集到目标链接，不设置complated!")
            self.browser.close()
