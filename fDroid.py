from urllib import request,parse
from http import cookiejar
import json,re,requests,sys,codecs,time,urllib
from bs4 import BeautifulSoup

user_agent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:50.0) Gecko/20100101 Firefox/50.0'
localPath = '/home/gsm/fDroid'

resDict = dict()

def parser(data):
	res = dict()
	soup = BeautifulSoup(data, "lxml")
	targets = soup.find_all('li', class_ = 'package-link')
	for target in targets:
		if "许可证类型" in target.contents[0]:
			license = target.find('a').string
	# there're several versions of one app
	versions_list = soup.find(class_="package-versions-list")
	versions_list = versions_list.find_all(class_ = 'package-version')
	for version_infos in versions_list:
		#print ('----version', version)
		version = version_infos.find(class_ = 'package-version-header').find('a')['name']
		res[version] = dict()
		#print ('-----downloading source code')
		#downloading the source code of each version
		source_codeurl = version_infos.find(class_ = 'package-version-source').find('a')['href']
		r = requests.get(source_codeurl)
		codepath = localPath + '/code/'+ source_codeurl.replace('https://f-droid.org/repo/','')
		'''with open(codepath, "wb") as fout:
			for chunk in r.iter_content(chunk_size=204800):
				if chunk:
					fout.write(chunk)
					fout.flush()'''
		#downloading the apkfile of each version
		#print ('-----downloading apkfile')
		apkfile_url = version_infos.find(class_ = 'package-version-download').find('a')['href']
		r = requests.get(apkfile_url)
		apkpath = localPath + '/apk/' + apkfile_url.replace('https://f-droid.org/repo/','')
		'''with open(apkpath, "wb") as fout:
			for chunk in r.iter_content(chunk_size=204800):
				if chunk:
					fout.write(chunk)
					fout.flush()'''
		#get the permissions of each apk
		permissions_list = version_infos.find(class_ = 'package-version-permissions-list').find_all('li')
		permission_str = ''
		for permission_struct in permissions_list:
			permission = permission_struct.string.replace(' ','').replace('\r','').replace('\n','').replace('\t','')
			permission_str = permission_str + permission + ';'
		permission_str = permission_str[0:-1]
		res[version]['codepath'] = codepath
		res[version]['apkpath'] = apkpath
	return res



def get_info(package_name, Appurl):
	res = dict()
	print (package_name)
	req = request.Request(Appurl)
	req.add_header('User-Agent', user_agent)
	web = request.urlopen(req, timeout=30)
	charset = str(web.headers.get_content_charset())
	if charset == "None": charset = "utf-8"
	data = web.read().decode(charset)
	infos = parser(data)
	res[package_name] = infos
	return res



def get_list(Listurl):
	res = dict()
	package_preffix = 'https://f-droid.org'
	req = request.Request(Listurl)
	req.add_header('User-Agent', user_agent)
	web = request.urlopen(req, timeout=30)
	charset = str(web.headers.get_content_charset())
	if charset == "None": charset = "utf-8"
	data = web.read().decode(charset)
	soup = BeautifulSoup(data, "lxml")
	# get the applist
	applist = soup.find(id = 'full-package-list')
	applist = applist.find_all('a', class_ = 'package-header')
	for app in applist:
		package_name = app.find(class_ = 'package-name').get_text().replace('\n','').replace('\t','').replace(' ','')
		package_urlsuffix = app['href']
		res.update(get_info(package_name, package_preffix + package_urlsuffix))
	return res


Url_preffix = 'https://f-droid.org/zh_Hans/packages/'
res = dict()
# get the html
for i in range(1,2):
	if i == 1:
		url_suffix = ''
	else:
		url_suffix = str(i) + '/index.html'
	res.update(get_list(Url_preffix + url_suffix))	
# write the results to a json file
jsObj = json.dumps(res)
fileObject = open('jsonFile.json', 'w')  
fileObject.write(jsObj)  
fileObject.close()
