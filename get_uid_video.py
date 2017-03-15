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
	'Accept-Language':'zh-cn',
	'Accept-Encoding':'gzip, deflate',
}
baseurl = 'http://91p05.space/'

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
			f.writelines(key + ':' + cookie_dict[key]  + '\n')
	f.close()

# 从文件读取cookies
def get_cookies():
	with open('91_cookies','r') as f:
		cookies = {}
		for line in f.readlines():
			name,value = line.strip().split(':',1)
			cookies[name] = value
	f.close()
	cookies = requests.utils.cookiejar_from_dict(cookies, cookiejar=None, overwrite=True)
	return cookies

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
	login_page = s.post(posturl,data=postdata,headers=head)
	cookie_dict = requests.utils.dict_from_cookiejar(s.cookies)
	save_cookies(cookie_dict)


# 判断是否已经登录
def isLogin():
	head = {
		'User-Agent':"User-Agent:Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
	}
	islogin_url = 'http://91p05.space/my_profile.php'
	login_code = s.get(islogin_url,headers = head)
	soup = BeautifulSoup(login_code.content,'lxml')
	pattern = r'http://91p05\.space/signup\.php'
	signup = re.findall(pattern,str(soup))
	# print signup
	if len(signup):
		return False
	else:
		return True

# 下载视频
def getvideo(filename,url):
	pwd = os.getcwd() + '/uid_video/'
	filename = pwd + filename
	with closing(s.get(url, stream=True)) as response:
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
	r = s.get(hot_url,headers=head)
	r.encoding = 'utf8'
	soup = BeautifulSoup(r.content,'lxml')
	tag_a = soup.find(id="fullbox-content").find('table').find_all('a')
	href_list = []
	for a in tag_a:
		pattern = r'<a href="(.+viewkey[^\"]+)"'
		href = re.match(pattern,a.encode('utf8'))
		if href is not None:
			h = href.groups()
			if h[0] not in href_list:
				href_list.append(h[0])
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
	soup = BeautifulSoup(r.content,'lxml')
	pattern = r'so\.addVariable\(\'file\',\'([0-9]+)\'\)'
	VID = re.findall(pattern,str(soup))
	pattern = r'so\.addVariable\(\'max_vid\',\'([0-9]+)\'\)'
	max_vid = re.findall(pattern,str(soup))
	pattern = r'so\.addVariable\(\'seccode\'[\s,]+\'(\w+)\'\)'
	seccode = re.findall(pattern,str(soup))
	url = baseurl + 'getfile.php?VID=' + VID[0] + '&mp4=0&seccode=' + seccode[0] + '&max_vid=' + max_vid[0]
	heads = {
		'Host':'91p05.space',
		'Referer':page_url,
		'User-Agent':"User-Agent:Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
		'Accept':'*/*',
		'Cookie':'__utma=214804319.94945956.1488175943.1488328495.1488333076.7; __utmb=214804319.0.10.1488333076; __utmc=214804319; __utmz=214804319.1488175943.1.1.utmcsr=91dizhi.space|utmccn=(referral)|utmcmd=referral|utmcct=/; __cfduid=d36fc2e7a2495332d55c489562c34f3d81488175942; AJSTAT_ok_pages=3; AJSTAT_ok_times=7; watch_times=2; CLIPSHARE=84ju84jitsj6qj55j5fe37efi6; show_msg=1; 91username=hu0097',
		'Accept-Language':'zh-cn',
		'Accept-Encoding':'gzip, deflate',
	}
	r = s.get(url,headers=heads)
	r.encoding='utf8'
	url_list = r.text.split('&')
	name,value = url_list[0].split('=',1)
	url = urllib.unquote(value)
	video_info.append(url)
	return video_info

def isExist(filename):
	pwd = os.getcwd() + '/uid_video/'
	if os.path.isdir(pwd):
		for s in os.listdir(pwd):
			# print unicode(s,'utf8')
			# print filename
			if unicode(s,'utf8') == filename:
				return True
			else:
				continue

# 保存已下载的url
def save_url(filename,video_url):
	with open('url_file.txt','wb') as f:
		f.writelines(filename + ':' + video_url  + '\n')
	f.close()
	
if __name__ == '__main__':
	s = requests.Session()
	try:
		s.cookies = get_cookies()
	except:
		# login()
		pass
	if isLogin():
		print('您已经登录')
		# watch_url = 'http://91p05.space/v.php?next=watch'
		# hot_url = get_hot(watch_url)
		# print hot_url[5]
		# page_url = get_page_url(hot_url[5])
		# for purl in page_url:
		# 	video_info = get_file(purl)
		# 	filename = video_info[0] + '.mp4'
		# 	video_url = video_info[1]
		# 	save_url(filename,video_url)
		# 	if isExist(filename):
		# 		print 'the file is exist'
		# 	else:
		# 		print 'not exist'
		# 		getvideo(filename,video_url)
		# url = 'http://91p05.space/uvideos.php?UID=3413087&type=public'
		# r = s.get(url,headers=head)
		# r.encoding = 'utf8'
		# with open('./21.html','wb') as f:
		# 	f.write(r.content)
		# 	f.close()
		# f = open('./21.html','r')
		# soup = BeautifulSoup(f.read(),'lxml')
		# tag_a = soup.find(id='myvideo-content').find_all('a')
		# print tag_a
		# for a in (1,3,5,7):
		# 	print tag_a[a].get('href')
		# 	print tag_a[a].string
		# url = 'http://91p05.space/uvideos.php?UID=3413087&type=public&page='
		# url = 'http://91p05.space/uvideos.php?UID=364868&type=public'
		# url = 'http://91p05.space/uvideos.php?UID=3181841&type=public&page='
		# url = 'http://91p05.space/uvideos.php?UID=3270831&type=public&page='
		# url = 'http://91p05.space/uvideos.php?UID=3931208&type=public&page='
		# url = 'http://91p05.space/uvideos.php?UID=4523057&type=public&page='
		# url = 'http://91p05.space/uvideos.php?UID=2527420&type=public&page='
		# url = 'http://91p05.space/uvideos.php?UID=4279628&type=public&page='
		# url = 'http://91p05.space/uvideos.php?UID=3948336&type=public&page='
		# url ='http://91p05.space/uvideos.php?UID=4966079&type=public'
		# url = 'http://91p05.space/uvideos.php?UID=3705078&type=public'
		# url = 'http://91p05.space/uvideos.php?UID=1081931&type=public&page='
		# url = 'http://91p05.space/uvideos.php?UID=830556&type=public&page='
		# url = 'http://91p05.space/uvideos.php?UID=33043&type=public&page='
		# url = 'http://91p05.space/uvideos.php?UID=3931208&type=public&page='
		# url = 'http://91p05.space/uvideos.php?UID=2466899&type=public&page='
		# url = 'http://91p05.space/uvideos.php?UID=1138117&type=public&page='
		# url = 'http://91p05.space/uvideos.php?UID=311463&type=public&page='
		# url = 'http://91p05.space/uvideos.php?UID=64657&type=public&page='
		# url = 'http://91p05.space/uvideos.php?UID=779233&type=public&page='
		# url = 'http://91p05.space/uvideos.php?UID=3823709&type=public&page='
		# url = 'http://91p05.space/uvideos.php?UID=2890367&type=public&page='
		# url = 'http://91p05.space/uvideos.php?UID=2518484&type=public&page='
		# url = 'http://91p05.space/uvideos.php?UID=1754938&type=public&page='
		# url = 'http://91p05.space/uvideos.php?UID=3073259&type=public&page='
		# url = 'http://91p05.space/uvideos.php?UID=3229116&type=public&page='
		# url = 'http://91p05.space/uvideos.php?UID=3584272&type=public&page='
		# url = 'http://91p05.space/uvideos.php?UID=3333601&type=public&page='
		# url = 'http://91p05.space/uvideos.php?UID=1810763&type=public&page='
		# url = 'http://91p05.space/uvideos.php?UID=5906392&type=public&page='
		# url = 'http://91p05.space/uvideos.php?UID=4667894&type=public&page='
		# url = 'http://91p05.space/uvideos.php?UID=2812257&type=public&page='
		# url = 'http://91p05.space/uvideos.php?UID=4222089&type=public&page='
		url = 'http://91p05.space/uvideos.php?UID=4395097&type=public&page='
		# r = s.get(url,headers=head)
		# r.encoding = 'utf8'
		# soup = BeautifulSoup(r.content,'lxml')
		# tag_a = soup.find(id='myvideo-content').find_all('a')
		# for a in (1,3,5,7):
		# 	time.sleep(2)
		# 	print tag_a[a].get('href')
		# 	mp4name = tag_a[a].string + '.mp4'
		# 	print mp4name
		# 	if isExist(mp4name):
		# 		print 'the file is exist'
		# 	else:
		# 		print 'not exist'
		# 		video_info = get_file(tag_a[a].get('href'))
		# 		video_url = video_info[1]
		# 		filename = video_info[0] + '.mp4'
		# 		save_url(filename,video_url)
		# 		getvideo(mp4name,video_url)



		# 从用户的视频列表界面下载视频
		for i in range(12):
			page_url = url + str(i+1)
			# print page_url
			r = s.get(page_url,headers=head)
			r.encoding = 'utf8'
			soup = BeautifulSoup(r.content,'lxml')
			tag_a = soup.find(id='myvideo-content').find_all('a')
			for a in (1,3,5,7,9):
				# time.sleep(2)
				print tag_a[a].get('href')
				mp4name = tag_a[a].string + '.mp4'
				print mp4name
				if isExist(mp4name):
					print 'the file is exist'
				else:
					print 'not exist'
					video_info = get_file(tag_a[a].get('href'))
					video_url = video_info[1]
					filename = video_info[0] + '.mp4'
					save_url(filename,video_url)
					getvideo(mp4name,video_url)

		# # 从视频页面下载视频
		# url = 'http://91p05.space/view_video.php?viewkey=b388ed67d8e0f180f3fe'
		# url = 'http://91p05.space/view_video.php?viewkey=fe16467e9707b5d7ef0a'
		# url = 'http://91p05.space/view_video.php?viewkey=f3328567e249fd99ef54'
		# url = 'http://91p05.space/view_video.php?viewkey=d95acaa132aa3b8b1769'
		# url = 'http://91p05.space/view_video.php?viewkey=dfd36e41ecc9fc8680c8'
		# url = 'http://91p05.space/view_video.php?viewkey=a9a811375e675b36d5ab&page=62&viewtype=basic&category=mf'
		# url = 'http://91p05.space/view_video.php?viewkey=dc6bf5a961d828791c66'
		# url = 'http://91p05.space/view_video.php?viewkey=772c447c66730b0cb911&page=65&viewtype=basic&category=mf'
		# url = 'http://91p05.space/view_video.php?viewkey=707ed4444996ef419613&page=67&viewtype=basic&category=mf'
		# url = 'http://91p05.space/view_video.php?viewkey=fe8898b8e28ab61d0a38&page=74&viewtype=basic&category=mf'
		# url = 'http://91p05.space/view_video.php?viewkey=e1032071f35c725ea788'
		# url = 'http://91p05.space/view_video.php?viewkey=06aaf81430a1500f9366'
		# url = 'http://91p05.space/view_video.php?viewkey=9d7dc6fe13db9bd50a32&page=105&viewtype=basic&category=mf'
		# url = 'http://91p05.space/view_video.php?viewkey=50b35f16a25b02173971&page=107&viewtype=basic&category=mf'
		# url = 'http://91p05.space/view_video.php?viewkey=441b2de263b955ab8a6a'
		# url = 'http://91p05.space/view_video.php?viewkey=32c125ce37daf4473f05'
		# url = 'http://91p05.space/view_video.php?viewkey=f92ddab9aa72b10ea8e7'
		# url = 'http://91p05.space/view_video.php?viewkey=d078f77361620c9481ff'
		# url = 'http://91p05.space/view_video.php?viewkey=1e5190a52bc01c17c82a'
		# url = 'http://91p05.space/view_video.php?viewkey=bc3419466d5a8a7d40c5&page=131&viewtype=basic&category=mf'
		# url = 'http://91p05.space/view_video.php?viewkey=b5f24ad29f8d5e9ab3dd'
		# video_info = get_file(url)
		# video_url = video_info[1]
		# filename = video_info[0] + '.mp4'
		# save_url(filename,video_url)
		# getvideo(filename,video_url)




				# video_info = get_file(tag_a[a].get('href'))
				# filename = video_info[0] + '.mp4'
				# video_url = video_info[1]
				# save_url(filename,video_url)
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

















