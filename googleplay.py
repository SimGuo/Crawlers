from urllib import request,parse
from http import cookiejar
import json,re,requests,sys,codecs,time,urllib

infile = sys.argv[1] + '.csv'
outfile = sys.argv[1] + '_res.csv'
outfile2 = sys.argv[1] + '_error.csv'


with codecs.open(infile, 'r', 'utf-8') as fin:
	with codecs.open(outfile, 'w', 'utf-8') as fout:
		with codecs.open(outfile2, 'w', 'utf-8') as fout2:
			for package_name in fin:
				package_name = package_name.replace("\n","")[1:-2]
				# prepare the cookie
				Referer_url = 'https://play.google.com/store/apps/details?id=' + package_name
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
					'Referer':Referer_url,
					'Cookie': str_cookie,
					'Connection':'keep-alive',
					'Pragma':'no-cache',
					'Cache-Control':'no-cache'
				}
				postdata={
					'hl' : 'en',
					'ids': package_name,
					'xhr':"1"
				}

				# post the data and get the responce
				url = 'https://play.google.com/store/xhr/getdoc?authuser=0'
				postdata = parse.urlencode(postdata)
				postdata = postdata.encode('utf-8')
				req = request.Request(url,postdata,header)
				try:
					r = request.urlopen(req)
				except urllib.error.URLError as e:
					fout2.write(package_name + ',' + 'URLError\n')
					continue

				# get the related part in the responce
				source = r.read().decode('utf-8')
				source2 = source.replace("\n", "")
				if source2[0:4] == ')]}\'':
					source2 = source2[4:]
				else:
					fout2.write(package_name + ', responce error\n')
					continue
				source2 = json.loads(source2)
				target_dict = source2[0][-1][0][-1]
				target_list = list(target_dict.values())[0]
				reslist = target_list[-1]

				# get the result from each element in the list
				res = set()
				if len(reslist) > 3 and isinstance(reslist[0],list):
					son_reslist = reslist[0]
					for elem in son_reslist:
						if len(elem) > 0:
							targets = elem[1]
							for target in targets:
								res.add(target[0])
					son_reslist = reslist[1]
					for elem in son_reslist:
						if len(elem) > 0:
							targets = elem[1]
							for target in targets:
								res.add(target[0])			
					son_reslist = reslist[2]
					for elem in son_reslist:
						if len(elem) > 1:
							target = elem[0]
							res.add(target)
				else:
					fout2.write(package_name + ', responce error Two\n')
					continue

				str_res = ''
				for elem in res:
					str_res = str_res + elem + ';'
				str_res = str_res[0:-1]

				fout.write(package_name + ',' + str_res + '\n')
