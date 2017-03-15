# -*- coding: utf-8 -*-
import certifi
import requests
import cookielib
import urllib3.contrib.pyopenssl
import os.path
import re
import os
import urllib
import time
from contextlib import closing
from bs4 import BeautifulSoup
try:
	from PIL import Image
except:
	pass

class ProgressBar(object):
	def __init__(self, title,
				count=0.0,
				run_status=None,
				fin_status=None,
				total=100.0,
				unit='', sep='/',
				chunk_size=1.0):
		super(ProgressBar, self).__init__()
		self.info = "【%s】%s %.2f %s %s %.2f %s"
		self.title = title
		self.total = total
		self.count = count
		self.chunk_size = chunk_size
		self.status = run_status or ""
		self.fin_status = fin_status or " " * len(self.statue)
		self.unit = unit
		self.seq = sep

	def __get_info(self):
		# 【名称】状态 进度 单位 分割线 总数 单位
		_info = self.info % (self.title.encode('utf-8'), self.status,self.count/self.chunk_size, self.unit, self.seq, self.total/self.chunk_size, self.unit)
		return _info

	def refresh(self, count=1, status=None):
		self.count += count
		# if status is not None:
		self.status = status or self.status
		end_str = "\r"
		if self.count >= self.total:
			end_str = '\n'
			self.status = status or self.fin_status
		print self.__get_info() + end_str

head = {
	'User-Agent':"User-Agent:Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
	# 'Accept':"text/plain, */*; q=0.01",
	'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6',
	'Accept-Encoding':'gzip, deflate',
}
# head = {
# 		'User-Agent':"User-Agent:Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
# 		'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
# 		# 'Cookie':'__utma=214804319.94945956.1488175943.1488328495.1488333076.7; __utmb=214804319.0.10.1488333076; __utmc=214804319; __utmz=214804319.1488175943.1.1.utmcsr=91dizhi.space|utmccn=(referral)|utmcmd=referral|utmcct=/; __cfduid=d838b0f51aea89afe5126deeb0d1e3c161488504611; AJSTAT_ok_pages=3; AJSTAT_ok_times=7; watch_times=1; CLIPSHARE=0gdms9fbju2olj7c241viq6iu6; show_msg=1; 91username=hu8350838',
# 		'Accept-Language':'en_US',
# 		'Referer':'http://91p05.space/v.php?next=watch',
# 		'Accept-Encoding':'gzip, deflate, sdch',
# 	}
baseurl = 'http://91p05.space/'
# url = 'http://www.91porn.com/view_video.php?viewkey=fde71b7a71661cc5816e&page=9&viewtype=basic&category=mf'
# url = 'http://www.91porn.com/index.php'
# url = 'http://91p05.space/login.php'
# url = 'https://www.youtube.com'
# url = 'https://www.zhihu.com'
# s = requests.Session()
# s.cookies = cookielib.LWPCookieJar('91cookies')
# try:
# 	s.cookies.load(ignore_discard=True)
# 	print('Cookie 已加载')
# except:
# 	print("Cookie 未能加载")

# 获得验证码
def get_captcha():
	captcha_url = 'http://91p05.space/captcha.php';
	r = s.get(captcha_url,headers=head);
	with open('./captcha.jpg','wb') as f:
		f.write(r.content)
		f.close()
	try:
		im = Image.open('captcha.jpg')
		im.show()
		im.close()
	except:
		print(u'请到 %s 目录找到captcha.jpg 手动输入' % os.path.abspath('captcha.jpg'))
	captcha = input("please input the captcha\n>")
	return captcha

# 保存cookies
def save_cookies(cookie_dict):
	with open('91_cookies','wb') as f:
		for key in cookie_dict:
			# print key + ':' + cookie_dict[key]
			f.writelines(key + ':' + cookie_dict[key]  + '\n')
	f.close()

# 从文件读取cookies
def get_cookies():
	try:
		with open('91_cookies','r') as f:
			cookies = {}
			for line in f.readlines():
				# print line
				name,value = line.strip().split(':',1)
				cookies[name] = value
		f.close()
		cookies = requests.utils.cookiejar_from_dict(cookies, cookiejar=None, overwrite=True)
		return cookies
	except:
		print '无法找到cookies文件，正在重新登录'
		login()

# 登录
def login():
	posturl = 'http://91p05.space/login.php'
	postdata = {
				'username':'',
				'password':'',
				'fingerprint':'1218053133',
				'fingerprint2':'96c22848f2da14f6174fec1d1104c296',
				'captcha_input':get_captcha(),
				'action_login':'Log In',
				'x':0,
				'y':0,
	}
	# print s.cookies
	login_page = s.post(posturl,data=postdata,headers=head)

	# print login_page.cookies
	cookie_dict = requests.utils.dict_from_cookiejar(s.cookies)
	# print cookie_dict
	save_cookies(cookie_dict)
	# cookies = requests.utils.cookiejar_from_dict(cookie_dict, cookiejar=None, overwrite=True)
	# print cookies
	# r = s.get('http://91p05.space/my_profile.php',headers=head,cookies=cookies)
	# print s.cookies

	# help(cookies)
	# cookies.save('91cookies1')
	# print(login_page.status_code)
	login_page.encoding = 'utf8'
	with open('26.html','wb') as f:
		f.write(login_page.text.encode('utf8'))
		f.close()
	# s.cookies.save()

# 判断是否已经登录
def isLogin():
	head = {
		'User-Agent':"User-Agent:Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
	}
	islogin_url = 'http://91p05.space/my_profile.php'
	login_code = s.get(islogin_url,headers = head)
	# # print login_code
	# # with open('17.html','wb') as f:
	# # 	f.write(login_code.content)
	# # 	f.close()
	# if login_code.status_code == 200:
	# 	return True
	# else:
	# 	return False

	# f = open('./17.html')
	soup = BeautifulSoup(login_code.content,'lxml')
	pattern = r'http://91p05\.space/signup\.php'
	signup = re.findall(pattern,str(soup))
	print signup
	if len(signup):
		return False
	else:
		return True

# 下载视频
def getvideo(filename,url):
	pwd = os.getcwd() + '/video/'
	filename = pwd + filename
	with closing(s.get(url,headers = head, stream=True)) as response:
		chunk_size = 1024 # 单次请求最大值
		content_size = int(response.headers.get('Content-Length')) # 内容体总大小
		progress = ProgressBar(filename, total=content_size,
										unit="KB", chunk_size=chunk_size, run_status="正在下载", fin_status="下载完成")
		with open(filename, "wb") as file:
			for data in response.iter_content(chunk_size=chunk_size):
				file.write(data)
				progress.refresh(count=len(data))

# 从视频页面获得收藏最多 最火等页面的链接
def get_hot(watch_url):
	url = watch_url
	r = s.get(url,headers = head)
	r.encoding = 'utf8'
	soup = BeautifulSoup(r.content,'lxml')
	tag_a = soup.find(id="navsubbar").find_all('a')

	href = [];
	for a in range(len(tag_a)):
		href.append(tag_a[a].get('href'))
	# print href
	return href

#从收藏最多页面获得各个视频的链接一页一共有20个视频链接
def get_page_url(hot_url):
	# f = open('./20.html')
	r = s.get(hot_url,headers=head)
	r.encoding = 'utf8'
	soup = BeautifulSoup(r.content,'lxml')
	# tag_a = soup.find(id="fullbox-content").find_all('a')
	tag_a = soup.find(id="fullbox-content").find('table').find_all('a')
	href_list = []
	for a in tag_a:
		pattern = r'<a href="(.+viewkey[^\"]+)"'
		href = re.match(pattern,a.encode('utf8'))
		if href is not None:
			h = href.groups()
			if h[0] not in href_list:
				href_list.append(h[0])
	# f.close()
	return href_list

# 通过播放器页面获得文件的相关链接信息如VID seccode max_vid等等
def get_file(page_url):
	video_info = []
	r = s.get(page_url,headers=head)
	r.encoding = 'utf8'
	soup = BeautifulSoup(r.content,'lxml')
	strip_name = soup.title.string.strip()
	name = strip_name.split('-')
	filename = name[0].strip()
	video_info.append(filename)
	# print filename
	# with open('20.html','wb') as f:
	# 	f.write(r.text.encode('utf8'))
	# 	f.close()
	soup = BeautifulSoup(r.content,'lxml')
	# VID = soup.find_all(re.compile('<script.+'))
	pattern = r'so\.addVariable\(\'file\',\'([0-9]+)\'\)'
	VID = re.findall(pattern,str(soup))
	# print VID[0]
	pattern = r'so\.addVariable\(\'max_vid\',\'([0-9]+)\'\)'
	max_vid = re.findall(pattern,str(soup))
	# print max_vid[0]
	pattern = r'so\.addVariable\(\'seccode\'[\s,]+\'(\w+)\'\)'
	seccode = re.findall(pattern,str(soup))
	# print seccode[0]
	url = baseurl + 'getfile.php?VID=' + VID[0] + '&mp4=0&seccode=' + seccode[0] + '&max_vid=' + max_vid[0]
	# print url
	# payload = {'VID':VID[0],'mp4':0,'seccode':seccode[0],'max_vid':max_vid[0]}
	heads = {
		'Host':'91p05.space',
		'Referer':page_url,
		'User-Agent':"User-Agent:Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
		# 'Accept':"text/plain, */*; q=0.01",
		'Accept':'*/*',
		'Cookie':'__utma=214804319.94945956.1488175943.1488328495.1488333076.7; __utmb=214804319.0.10.1488333076; __utmc=214804319; __utmz=214804319.1488175943.1.1.utmcsr=91dizhi.space|utmccn=(referral)|utmcmd=referral|utmcct=/; __cfduid=d36fc2e7a2495332d55c489562c34f3d81488175942; AJSTAT_ok_pages=3; AJSTAT_ok_times=7; watch_times=2; CLIPSHARE=84ju84jitsj6qj55j5fe37efi6; show_msg=1; 91username=hu0097',
		'Accept-Language':'zh-cn',
		'Accept-Encoding':'gzip, deflate',
	}
	r = s.get(url,headers=heads)
	r.encoding='utf8'
	# print r.text
	# return r.text
	url_list = r.text.split('&')
	# print url_list
	name,value = url_list[0].split('=',1)
	url = urllib.unquote(value)
	video_info.append(url)
	# return urllib.unquote(value)
	return video_info

def isExist(filename):
	pwd = os.getcwd() + '/video/'
	if os.path.isdir(pwd):
		# print os.listdir(pwd)
		for s in os.listdir(pwd):
			# print filename
			# print s
			if unicode(s,'utf8') == filename:
				return True
			else:
				continue

# 保存已下载的url
def save_url(filename,video_url):
	with open('url_file','wb') as f:
		f.writelines(filename + ':' + video_url  + '\n')
	f.close()
	


# proxy = {'http':'http://hu0097@163.com:Hu192218@47.90.60.147:11090/','https':'http://hu0097@163.com:Hu192218@47.90.60.147:11090/'}
# proxy = {'http':'socks5://hu0097@163.com:Hu192218@120.25.202.132:11090/'}
# r = s.get(url=url,headers=head)
# print r.status_code
# with open('333.html','wb') as f:
# 	f.write(r.content)
# 	f.close()
# print get_captcha()

# http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',ca_certs=certifi.where())
# r = http.request('GET',url)
# with open('111.html','wb') as f:
# 	f.write(r.data)
# 	f.close()

# login()
if __name__ == '__main__':
	s = requests.Session()
	s.cookies = get_cookies()
	if isLogin():
		print('您已经登录')
		watch_url = 'http://91p05.space/v.php?next=watch'
		hot_url = get_hot(watch_url)
		head1 = {
			'User-Agent':"User-Agent:Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
			'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
			# 'Cookie':'__utma=214804319.94945956.1488175943.1488328495.1488333076.7; __utmb=214804319.0.10.1488333076; __utmc=214804319; __utmz=214804319.1488175943.1.1.utmcsr=91dizhi.space|utmccn=(referral)|utmcmd=referral|utmcct=/; __cfduid=d838b0f51aea89afe5126deeb0d1e3c161488504611; AJSTAT_ok_pages=3; AJSTAT_ok_times=7; watch_times=1; CLIPSHARE=0gdms9fbju2olj7c241viq6iu6; show_msg=1; 91username=hu8350838',
			'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6',
			'Referer':'http://91p05.space/v.php?next=watch',
			'Accept-Encoding':'gzip, deflate, sdch',
		}
		hot = hot_url[5] + '&page=3'
		hot_page = s.get(hot,headers=head1)
		# print hot_page.encoding
		# print hot_page.apparent_encoding
		# with open('24.html','wb') as f:
		# 	f.write(hot_page.content)
		# 	f.close()
		hot_page.encoding = 'utf-8'
		# print hot_page.encoding
		# hot_page=str(hot_page.content,'utf-8')
		# with open('25.html','wb') as f:
		# 	f.write(hot_page.text.encode('utf-8'))
		# 	f.close()
		soup = BeautifulSoup(hot_page.text.encode('utf-8'),'lxml')
		tag_a = soup.find(id="fullbox-content")
		page_info = {}
		div = tag_a.select('.imagechannel')
		for a in div:
			page_info[a.find('a').find('img').get('title')] = a.find('a').get('href')
		hddiv = tag_a.select('.imagechannelhd')
		for a in hddiv:
			page_info[a.find('a').find('img').get('title')] = a.find('a').get('href')
		for i in page_info:
			time.sleep(2)
			print i
			print page_info[i]
			filename = i + '.mp4'
			if isExist(filename):
				print 'the file is exist'
			else:
				print 'not exist'
				video_info = get_file(page_info[i])
				getvideo(filename,video_info[1])




		# print hot_url[5]
		# page_url = get_page_url(hot_url[5])
		# for purl in page_url:
		# 	time.sleep(2)
		# 	video_info = get_file(purl)
		# 	filename = video_info[0] + '.mp4'
		# 	video_url = video_info[1]
		# 	save_url(filename,video_url)
			# if isExist(filename):
			# 	print 'the file is exist'
			# else:
			# 	print 'not exist'
			# 	getvideo(filename,video_url)

		


		# get_page_url()
		# f = open('./666.html')
		# soup = BeautifulSoup(f,'lxml')
		# tag_a = soup.find(id="navsubbar").find_all('a')
		# href = [];
		# for a in range(len(tag_a)):
		# 	href.append(tag_a[a].get('href'))
		# print href[5]
		# f.close()
		# getvideo(href[5])

		# watch_url = 'http://91p05.space/v.php?next=watch'
		# hot_url = get_hot(watch_url)
		# print hot_url[5]
		# page_url = get_page_url(hot_url[5])
		# # for purl in page_url:
		# # 	print purl
		# print page_url[0]
		# page_url = 'http://91porn.com/view_video.php?viewkey=500de3cb1cc0d0391e78&amp;page=1&amp;viewtype=basic&amp;category=mf'
		# file_url = get_file(page_url)
		# file_url = 'file=http://68.235.35.99/cheat.mp4&domainUrl=http://91porn.ro.lt&imgUrl=http://img.file.am/91porn/'
		# url = 'http%3A%2F%2F192.240.120.2%2Fmp43%2F102331.mp4%3Fst%3Dv9kuvznn5uUJcAbWL4up3g%26e%3D1488425476'
		# print urllib.unquote(url)

		# url = 'file=http%3A%2F%2F192.240.120.2%2Fmp43%2F102331.mp4%3Fst%3Dv9kuvznn5uUJcAbWL4up3g%26e%3D1488425476&domainUrl=http://91porn.ro.lt&imgUrl=http://img.file.am/91porn/>'
		# url_list = url.split('&')
		# print url_list
		# name,value = url_list[0].split('=',1)
		# print urllib.unquote(value)
		# f = open('14.html')
		# soup = BeautifulSoup(f.read(),'lxml')
		# strip_name = soup.title.string.strip()
		# filename = strip_name.split('-')
		# print filename[0].strip()
		# f.close()


		

		# f = open('./13.html')
		# soup = BeautifulSoup(f,'lxml')
		# # tag_a = soup.find(id="fullbox-content").find_all('a')
		# tag_a = soup.find(id="fullbox-content").find('table').find_all('a')
		# # print tag_a
		# print len(tag_a)
		# # print tag_a
		# href_list = []
		# for a in tag_a:
		# 	pattern = r'<a href="(.+viewkey[^\"]+)"'
		# 	href = re.match(pattern,a.encode('utf8'))
		# 	if href is not None:
		# 		h = href.groups()
		# 		print h[0]
		# 		if h[0] not in href_list:
		# 			href_list.append(h[0])
		# print href_list
		# print len(href_list)
		# 		# help(href.groups())
		# 	# print a.encode('utf8')
		# 	# gethref = BeautifulSoup(a.encode('utf8'),'lxml')
		# 	# print gethref.get('href')
		# print href_list[0]
		# getvideo(href_list[0])
		# f.close()

		# f = open('./15.html')
		# soup = BeautifulSoup(f,'lxml')
		# # VID = soup.find_all(re.compile('<script.+'))
		# pattern = r'so\.addVariable\(\'file\',\'([0-9]+)\'\)'
		# VID = re.findall(pattern,str(soup))
		# print VID[0]
		# pattern = r'so\.addVariable\(\'max_vid\',\'([0-9]+)\'\)'
		# max_vid = re.findall(pattern,str(soup))
		# print max_vid[0]
		# pattern = r'so\.addVariable\(\'seccode\'[\s,]+\'(\w+)\'\)'
		# seccode = re.findall(pattern,str(soup))
		# print seccode[0]


		# f = open('./888.html')
		# soup = BeautifulSoup(f,'lxml')
		# tag_a = soup.find_all('a')
		# with open('12.html','wb') as f:
		# 	f.write(str(tag_a.encode()))
		# 	f.close()
		# help(tag_a)
		# for a in tag_a:
			# print a.decode_contents(eventual_encoding='utf-8')
			# print a.get_text()
			# print unicode(a.get_text(), "gb2312")
			# help(a.get_text())
			# help(a)
			# print unicode(a.get_text(),'utf8')
			# print a.decode()

	else:
		login()
		print('未登录')

















