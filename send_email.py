# -*- coding: utf-8 -*-
"""
@author: zhongxinwang
@date: 2016-10-02
"""


import smtplib
from email.mime.text import MIMEText

_user = "52145263@qq.com"
_pwd  = "aaaaaaaa"
_to   = ["52145263@qq.com"]

msg = MIMEText("Test")
# 邮件主题
msg["Subject"] = "don't panic, this is a test"
# 发送人
msg["From"]    = _user
# 收件人
msg["To"]      = ";".join(_to)

try:
    s = smtplib.SMTP_SSL("smtp.qq.com", 465)
    s.login(_user, _pwd)
    s.sendmail(_user, _to, msg.as_string())
    s.quit()
    print "Success!"
except smtplib.SMTPException,e:
    print "Falied,%s"%e 
