from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait


def getUserFansPage(userHome,url):
	try:
		userHome.get(url)
		WebDriverWait(userHome,10)
		linkTag = userHome.find_element_by_partial_link_text('粉丝')

		content = userHome.find_elements_by_xpath('//*[@class="weibo-detail"]')
		print(len(content))
		details = []
		for detail in content:
			text = detail.text
			details.append(text)

		print(linkTag.text)
		link = linkTag.get_attribute('href')
		print(link)
		gender = getGender(userHome)
		return link,gender,details
	except NoSuchElementException:
		print("find data error in user home.")
		return None,None,None
	except WebDriverException:
		print("web driver exception in user home page.")
		return None,None,None

def getGender(brower):
	try:
		brower.find_element_by_xpath('//*[@class="icon icon-female"]')
		return 'female'
	except NoSuchElementException:
		return 'male'

def getUserFans(fansList,url):
	list = []
	try:
		fansList.get(url)
		WebDriverWait(fansList,10)
		users = fansList.find_elements_by_xpath('//*[@class="box-col item-list"]')
		print(len(users))
		for u in users:
			userLink = u.get_attribute('href')
			print(userLink)
			list.append(userLink)
	except NoSuchElementException:
		print("find data error in fans list.")
	except WebDriverException:
		print("web driver exception in fans list.")
	return list

def userID(url):
	return url.split('/')[-1]

def out2File(outFile, user, gender, data):
	for u in data:
		outFile.write(user+','+gender+','+userID(u)+'\n')
	outFile.flush()

def det2File(file,user,det):
	try:
		file.write('\n<user>\n')
		file.write('<id>'+user+'</id>\n')
		for d in det:
			file.write('<det>\n')
			file.write(d)
			file.write('\n</det>')
		file.write('\n<user>\n')
	except UnicodeEncodeError:
		print("unicode encode error in det2File.")
	except TypeError:
		print("type error in det2File.")



userHome = webdriver.Chrome()
fansList = webdriver.Chrome()

userData = {}

dataFile = '../data.csv'
outFile = open(dataFile,'w')
outFile.write('user,gender,fans\n')

weiboDetFile = '../det_data.xml'
detFile = open(weiboDetFile,'w')

startUrl = 'http://m.weibo.cn/u/3834520403'
startUserID = startUrl.split('/')[-1]

fansListUrl,gender,det = getUserFansPage(userHome,startUrl)
print(det)
det2File(detFile,startUserID,det)
if fansListUrl == None:
	print("start error.")
userData[startUserID] = getUserFans(fansList,fansListUrl)
out2File(outFile,startUserID,gender,userData[startUserID])

from collections import deque

waitGetUser = deque()
waitGetUser.append(startUserID)
userNum = 1
while len(waitGetUser) > 0:
	for link in userData[waitGetUser.popleft()]:
		id = userID(link)
		if id in userData:
			continue

		fansListUrl, gender, det = getUserFansPage(userHome,link)
		print(det)
		det2File(detFile,id,det)
		if fansListUrl == None:
			continue

		userData[id] = getUserFans(fansList,fansListUrl)

		out2File(outFile,id,gender,userData[id])

		userNum += 1
		print('user num:'+str(userNum))
		if userNum >= 1000:
			break

		waitGetUser.append(id)

userHome.close()
fansList.close()

outFile.close()



