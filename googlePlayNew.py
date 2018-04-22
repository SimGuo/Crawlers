from urllib import request,parse
from http import cookiejar
import json,re,requests,sys,codecs,time,urllib

def get_permission(package_name):
	Referer_url = 'https://play.google.com/store/apps/details?id=' + package_name

	# prepare the cookie
	s = requests.session()
	s.get(Referer_url)
	str_cookie = ""
	for cook in s.cookies:
		str_cookie = str_cookie + cook.name + '=' + cook.value + ';'
	str_cookie = str_cookie[0:-1]

	# prepare the header
	header={
		'Host':'play.google.com',
		'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0',
		'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		'Content-Type':'application/x-www-form-urlencoded',
		'charset':'utf-8',
		'Referer':'https://play.google.com/',
		'Cookie': str_cookie,
		'Connection':'keep-alive',
		'Pragma':'no-cache',
		'Cache-Control':'no-cache'
	}
	postdata={
		'f.req' : '[[[163726509,[{\"163726509\":[[null,[\"' + package_name + '\",7],[]]]}],null,null,0]]]'
	}

	# post the data and get the responce
	url = 'https://play.google.com/_/PlayStoreUi/data?ds.extension=163726509&hl=en-US&soc-app=121&soc-platform=1&soc-device=1&authuser&rt=c'
	postdata = parse.urlencode(postdata)
	postdata = postdata.encode('utf-8')
	req = request.Request(url,postdata,header)
	r = request.urlopen(req)
	source = r.read().decode('utf-8')

	source = source[6:]
	res = ''

	Strings = source.split('\n',1)
	if len(Strings) > 1:
		Num = int(Strings[0])
		LeftString = Strings[1]
		res += LeftString[0:Num-1]

	res =  json.loads(res)
	permissons = dict()
	targetfathers = res[0][2]['163726509']
	if len(targetfathers) > 0:
		targets = targetfathers[0]
		for element in targets:
			if len(element) > 0:
				keyword = element[0]
				permissons_group = element[2]
				temp_list = set()
				for permisson in permissons_group:
					temp_list.add(permisson[1])
				if keyword in permissons.keys():
					permissons[keyword].union(temp_list)
				else:
					permissons.update({keyword:temp_list})

	if len(targetfathers) > 1:
		temp_list = set()
		for element in targetfathers[1]:
			permissons_group = element[2]
			for permisson in permissons_group:
				temp_list.add(permisson[1])
		permissons.update({'Other':temp_list})

	if len(targetfathers) > 2:
		temp_list = set()
		permissons_group = targetfathers[2]
		for permisson in permissons_group:
			temp_list.add(permisson[1])
		permissons['Other'].union(temp_list)

	if len(permissons.keys()) > 0:
		return permissons
	else:
		return None


infile = '17noPerms.csv'
res = dict()
cnt = 0
with codecs.open(infile, 'r', 'utf-8') as fin:
	for package_name in fin:
		package_name = package_name.replace("\n","").replace('\"','')
		try:
			permissons = get_permission(package_name)
			if permissons != None:
				res[package_name] = permissons
			print ('-------------', cnt, '---------------')
			cnt += 1
			print (permissons)
		except:
			continue

resJson = json.dumps(res)

outfile = open('17noPerms.json','w')
outfile.write(resJson)
outfile.close()




