# !/usr/bin/python
# -*-coding: utf-8 -*-

import time
import smtplib
from email.mime.text import MIMEText
# 收件人列表
mailto_list = ["578337729@qq.com"]
# 发送服务器
mail_host = "smtp.qq.com"
# 端口号
mail_port = "465"
# 发件人用户名
mail_user = "578337729"
# qq邮箱授权码
mail_pass = "wgyjkszdvmpdbcai"
# 发送邮箱后缀
mail_postfix = "@qq.com"

# to_list：收件人, sub：主题, content：邮件内容
def send_mail(to_list, sub, content):
    sender = mail_user + mail_postfix
    # 实例，_subtype: 格式邮件, _charset: 字符编码
    msg = MIMEText(content, _subtype='html', _charset='utf-8')
    # 设置主题
    msg['Subject'] = sub
    # 日期
    # msg["Date"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    # 发件人
    msg['From'] = sender
    # 收件人
    msg['To'] = ";".join(to_list)
    print u"主题: " + msg['Subject']
    print u"发件人: " + msg['From']
    print u"收件人: " + msg['To']

    try:
        s = smtplib.SMTP_SSL()
        print u"---建立实例---"
        # 连接smtp服务器
        s.connect(host=mail_host, port=mail_port)
        print u"---连接成功---"
        # 登陆服务器(注: 公司邮箱服务器登录名不为邮箱地址!!!)
        s.login(mail_user, mail_pass)
        print u"---登录成功---"
        # 发送邮件
        s.sendmail(sender, to_list, msg.as_string())
        print u"---发送邮件---"
        s.close()
        return True
    except Exception, e:
        print e
        return False

if __name__ == '__main__':
    if send_mail(mailto_list, u"python群发邮件测试", u"<a href='http://blog.csdn.net/Marksinoberg/article/details/51501377'>测试链接</a>"):
        print u"发送成功"
    else:
        print u"发送失败"
