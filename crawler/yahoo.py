# coding = utf-8
import requests as rq
from bs4 import BeautifulSoup
import io
import os
import time
import re
from selenium import webdriver

URL = "https://tw.buy.yahoo.com/category/4385943"

# use number index save each class to single file
fileIndex = 1

def getProducts(url, cls):
	global fileIndex
	classesFile = io.open('./data/yahoo_classes%03d.csv'%fileIndex,'w')
	imagesFile = io.open('./data/yahoo_images%03d.csv'%fileIndex,'w')
	fileIndex += 1
	chrome_options = webdriver.ChromeOptions()
	prefs = {"profile.default_content_setting_values.notifications" : 2}
	chrome_options.add_experimental_option("prefs",prefs)
	driver = webdriver.Chrome('/home/kevin/bin/chromedriver',chrome_options=chrome_options)
	driver.get(url)
	page = 1

	while True:
		print("page:%d"%page)

		try:
			# sometimes it will return system busy, retry after 3 seconds
			driver.find_element_by_xpath('//span[contains(text(),"很抱歉，系統忙碌中，請您再搜尋一次。")]')
			print("system busy, retry!")
			time.sleep(3)
			driver.refresh()
			continue
		except:
			print('page is normal')

		# scroll to end to make all items visible
		for i in range(0,8):
			driver.execute_script("window.scrollTo(0, {});".format(1080*i))
			time.sleep(0.3)


		# start record data
		try:
			'''
				<div style="width:100%;-webkit-flex-shrink:0;flex-shrink:0;overflow:auto" aria-hidden="false" data-swipeable="true">
					<div class="SquareFence_wrap_3jTo2">
						<img alt="realme XT (8G/128G) 6.4吋6400萬畫素 四鏡頭鷹眼猛獸" srcset="https://s.yimg.com/zp/MerchandiseImages/2BDB8EDD5D-Product-24176800.jpg 1x, https://s.yimg.com/zp/MerchandiseImages/772B8A2228-Product-24176800.jpg 2x" decoding="async" src="https://s.yimg.com/zp/MerchandiseImages/2BDB8EDD5D-Product-24176800.jpg" class="SquareImg_img_2gAcq">
					</div>
				</div>
			'''
			count = 0
			for img in driver.find_elements_by_xpath('//div[@aria-hidden="false"]/div[@class="SquareFence_wrap_3jTo2"]/img'):
				name = img.get_attribute('alt').strip()
				classesFile.write("{}, {}\n".format(cls, name))
				imagesFile.write("{}, {}\n".format(name, img.get_attribute('src')))
				count+=1
			print("product count in page:%d"%count)
			page += 1
		except:
			print('error on find elements')

		# trigger next page
		try:
			nextPage = driver.find_element_by_xpath('//a[contains(@class,"Pagination__icoArrowRight___2KprV")]')
			classes = nextPage.get_attribute('class')
			# already reach last page, break this loop
			if(classes.find('Disabled') >= 0):
				break;

			nextPage.click()
			time.sleep(1)
		except:
			print('next page not exists, try to use url')
			pages = driver.find_elements_by_xpath('//div[@class="Pagination__numberContainer___2oWVw"]/a')
			if(page>len(pages)):
				print("reach last page, break loop")
				break
			driver.get(url+"?pg={}".format(page))

	driver.close()
	classesFile.close()
	imagesFile.close()

def getSecondClass(url):
	rsp = rq.get(url)
	soup = BeautifulSoup(rsp.text, 'lxml')

	for a in soup.select('a.track-category-item-link.level2-item-text'):
		print(a.get('href'))
		print(a.text)
		getProducts(a.get('href'), a.text)

def start():
	if not os.path.isdir('./data'):
		os.mkdir('./data')
	'''
		1st level class:手機/相機/耳機/穿戴
		url:https://tw.buy.yahoo.com/category/4385943
		1st level class:家電/電視/冷氣/冰箱
		url:https://tw.buy.yahoo.com/category/4387479
		1st level class:電腦/電競/遊戲/週邊
		url:https://tw.buy.yahoo.com/category/4385993
		1st level class:精品/黃金/珠寶/手錶
		url:https://tw.buy.yahoo.com/category/4385425
		1st level class:女裝/男裝/童裝
		url:https://tw.buy.yahoo.com/category/4385324
		1st level class:內衣/睡衣/塑身衣
		url:https://tw.buy.yahoo.com/category/28491077
		1st level class:女鞋/男鞋/箱包/配件
		url:https://tw.buy.yahoo.com/category/4385507
		1st level class:醫美/保養/彩妝/香水
		url:https://tw.buy.yahoo.com/category/4385588
		1st level class:日用清潔/洗沐/美髮
		url:https://tw.buy.yahoo.com/category/4436714
		1st level class:食品/飲料/零食/生鮮
		url:https://tw.buy.yahoo.com/category/4419983
		1st level class:養生/保健/纖體/醫療
		url:https://tw.buy.yahoo.com/category/28491560
		1st level class:婦幼/圖書/玩具/樂器
		url:https://tw.buy.yahoo.com/category/4385885
		1st level class:寵物/餐廚/開運/生活
		url:https://tw.buy.yahoo.com/category/29588048
		1st level class:家具/床墊/寢具/家飾
		url:https://tw.buy.yahoo.com/category/4387670
		1st level class:運動/休閒/健身/戶外
		url:https://tw.buy.yahoo.com/category/4436854
		1st level class:機車/導航/汽車百貨
		url:https://tw.buy.yahoo.com/category/4456828
		1st level class:餐券/泡湯/住宿/遊樂
		url:https://tw.buy.yahoo.com/category/28648498

	'''
	#rsp = rq.get(URL)
	#soup = BeautifulSoup(rsp.text,'lxml')
	# for a in soup.findAll('a',{'class':'track-category-list'}):
	# 	print('1st level class:%s'%a.text)
	# 	print('url:%s'%a.get('href'))
	getSecondClass('https://tw.buy.yahoo.com/category/4385943')
	getSecondClass('https://tw.buy.yahoo.com/category/4387479')
	getSecondClass('https://tw.buy.yahoo.com/category/4385993')
	getSecondClass('https://tw.buy.yahoo.com/category/4385425')
	getSecondClass('https://tw.buy.yahoo.com/category/4385324')
	getSecondClass('https://tw.buy.yahoo.com/category/28491077')
	getSecondClass('https://tw.buy.yahoo.com/category/4385507')
	getSecondClass('https://tw.buy.yahoo.com/category/4385588')
	getSecondClass('https://tw.buy.yahoo.com/category/4436714')
	getSecondClass('https://tw.buy.yahoo.com/category/4419983')
	getSecondClass('https://tw.buy.yahoo.com/category/28491560')
	getSecondClass('https://tw.buy.yahoo.com/category/4385885')

	getSecondClass('https://tw.buy.yahoo.com/category/4387670')
	getSecondClass('https://tw.buy.yahoo.com/category/4436854')
	getSecondClass('https://tw.buy.yahoo.com/category/4456828')
	getSecondClass('https://tw.buy.yahoo.com/category/28648498')

	# follow link not use same style as above links, manually handle it
	# getSecondClass('https://tw.buy.yahoo.com/category/29588048')
	getProducts("https://tw.buy.yahoo.com/category/4456706","寵物")
	getProducts("https://tw.buy.yahoo.com/category/4484788","寵物")
	getProducts("https://tw.buy.yahoo.com/category/4387690","餐廚生活")
	getProducts("https://tw.buy.yahoo.com/category/4387692","餐廚生活")
	getProducts("https://tw.buy.yahoo.com/category/4387694","餐廚生活")
	getProducts("https://tw.buy.yahoo.com/category/4481481","餐廚生活")
	getProducts("https://tw.buy.yahoo.com/category/31658662","餐廚生活")
	getProducts("https://tw.buy.yahoo.com/category/4481522","餐廚生活")
	getProducts("https://tw.buy.yahoo.com/category/4387691","餐廚生活")
	getProducts("https://tw.buy.yahoo.com/category/4481536","餐廚生活")
	getProducts("https://tw.buy.yahoo.com/category/31658727","餐廚生活")

start()