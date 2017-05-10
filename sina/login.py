#coding: utf-8
#date: 2015-10-18
#mail: artorius.mailbox@qq.com
#author: xinwangzhong -version 0.1

import cookielib
import binascii
import chardet
import urllib2
import urllib
import random
import base64
import Image
import time
import rsa
import sys
import re
import os

reload(sys)
sys.setdefaultencoding('utf8')

class Login(object):
	"""docstring for Login"""

	def __init__(self, username, password):
		self.username = username
		self.password = password
		self.pcid = ""
		cj = cookielib.CookieJar()
		cookie_support = urllib2.HTTPCookieProcessor(cj)

		# 添加代理ip
		proxy_enabled = 0
		self.iplist = []
		try:
			cur_dir = os.path.dirname(os.path.realpath(__file__))
			for line in open(os.path.join(cur_dir, r'f:/getip.ip'), 'r'):
				self.iplist += [line.strip()]
		except IOError:
			print "IOError in sethp opening getip.ip"
			pass
		if len(self.iplist) and proxy_enabled:
			ip = random.choice(self.iplist)
			print ip, type(ip)
			proxy_support = urllib2.ProxyHandler({'http':'http://'+ip})
			# self.opener = urllib2.build_opener( proxy_support, cookie_support, urllib2.HTTPHandler)
			self.opener = urllib2.build_opener( proxy_support, cookie_support, urllib2.HTTPHandler )
			# self.opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
			# self.opener = urllib2.build_opener(proxy)
		else:
			self.opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
		urllib2.install_opener(self.opener)

	def __get_spwd(self):
		rsaPublickey = int(self.pubkey, 16)
		key = rsa.PublicKey(rsaPublickey, 65537) #创建公钥
		message = self.servertime + '\t' + self.nonce + '\n' + self.password #拼接明文js加密文件中得到
		passwd = rsa.encrypt(message, key) #加密
		passwd = binascii.b2a_hex(passwd) #将加密信息转换为16进制。
		return passwd
 
	def __get_suser(self):
		username_ = urllib.quote(self.username)
		username = base64.encodestring(username_)[:-1]
		return username

	def __mtime(self): 
		'''Return the current time by milli-second''' 
		return long('%.0f' % (time.time() * 1000))

	def __prelogin(self):
		pre_postdata = {
			"entry":"weibo",
			"callback":"sinaSSOController.preloginCallBack",
			"su": self.__get_suser(),
			"rsakt":"mod",
			"checkpin":"1",
			"client":"ssologin.js(v1.4.18)",
			"_": str(self.__mtime()),
		}
		# print pre_postdata
		# print urllib.urlencode(pre_postdata)
		pre_headers = {
			"Accept":"*/*",
			# "Accept-Encoding":"gzip, deflate, sdch",
			"Accept-Language":"zh-CN,zh;q=0.8",
			"Connection":"keep-alive",
			"Referer":"http://weibo.com/?c=spr_web_sq_kings_weibo_t001",
			"Host":"login.sina.com.cn",
			'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.154 Safari/537.36 LBBROWSER', 
		}
		prelogin_url = "http://login.sina.com.cn/sso/prelogin.php"
		pre_req = urllib2.Request(
			url = prelogin_url,
			data = urllib.urlencode(pre_postdata),
			headers = pre_headers
		)
		pre_response = self.opener.open(pre_req)
		html = pre_response.read()
		# print len(html)
		# print html#.decode("utf-8", "replace")+" "
		strurl = re.findall(r"\(([\s\S]*?)\)", html)
		dic = dict(eval(strurl[0])) #json格式的response
		self.pubkey = str(dic.get('pubkey'))
		self.servertime = str(dic.get('servertime'))
		self.nonce = str(dic.get('nonce'))
		self.rsakv = str(dic.get('rsakv'))
		self.pcid = str(dic.get("pcid"))
		self.showpin = str(dic.get("showpin"))
 
	def login(self):
		url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)'
		try:
			self.__prelogin() #预登录
		except Exception as e:
			print 'Prelogin Error', e
			return
		print "Prelogin Succeed"
		login_postdata = {
			'entry': 'weibo',
			'gateway': '1',
			'from': '',
			'savestate': '7',
			'useticket': '1',
			'pagerefer' : "",#'http://login.sina.com.cn/sso/logout.php?entry=miniblog&r=http%3A%2F%2Fweibo.com%2Flogout.php%3Fbackurl%3D%252F',
			'vsnf': '1',
			'service': 'miniblog',
			"su": "",#prelogin
			"sp": "",#prelogin
			"servertime": "",#prelogin
			"nonce": "",#prelogin
			'pwencode': 'rsa2',
			'rsakv' : "",#prelogin
			'encoding': 'UTF-8',
			'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
			'returntype': 'META',
			'prelt' : '1',
		}
		login_postdata['servertime'] = self.servertime
		login_postdata['nonce'] = self.nonce
		login_postdata['su'] = self.__get_suser()
		login_postdata['sp'] = self.__get_spwd()
		login_postdata['rsakv'] = self.rsakv
		if self.showpin == '1':
			code_url = "http://login.sina.com.cn/cgi/pin.php?p="+self.pcid+"&r=" + str(random.randint(20000000,99999999)) + "&s=0"
			data_pic = urllib2.urlopen(code_url).read()
			filename = "code.png"
			if os.path.isfile(filename):
				os.remove(filename)
			open(filename, "wb").write(data_pic)
			image = Image.open(filename)
			image.show()
			login_postdata["door"] = raw_input("code:").strip()
			login_postdata["pcid"] = self.pcid
			# login_postdata["sr"] = "1366*768"
		login_headers={
			'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.124 Safari/537.36', 
		}
		req = urllib2.Request(
			url = url,
			data = urllib.urlencode(login_postdata),
			headers = login_headers
		)
		response = self.opener.open(req)
		text = response.read()
		# print len(text), text.decode("GB2312", "replace")
		try:
			login_url = re.findall(r'location\.replace\([\'\"](.*?)[\'\"]\)', text.decode("GB2312", "replace"))[0]
			# print login_url
			retcode = re.findall(r"retcode=(\d+?)($|&)", login_url)[0][0]
			print "retcode: ", retcode
			req = urllib2.urlopen(login_url)
			# print req.info()
			# print req.read().decode("GB2312")
			if retcode == "0":
				print "Login Succeed"
			else:
				print 'Login Error, Error code ', retcode
		except KeyError:
			print 'Login Error'
			return None

if __name__ == '__main__':

	username = ''
	password = ''
	print "username:"+username
	weibo = Login(username, password)
	weibo.login()
