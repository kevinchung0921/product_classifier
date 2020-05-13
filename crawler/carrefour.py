# coding = utf-8
import requests as rq
from bs4 import BeautifulSoup
import io
import os
import time
import re
import json
import sys
from selenium import webdriver



BASE_URL = 'https://online.carrefour.com.tw/'


def start():
	global BASE_URL
	rsp = rq.get(BASE_URL)
	soup = BeautifulSoup(rsp.text, 'html.parser')
	startQuery = False
	for top1 in soup.findAll('div',{'class':'top1 left-item'}):
		for a in top1.findAll('a'):
			h3 = a.find('h3')
			if(h3 != None):
				mcls = h3.text.replace('．','')
				path = a.get('href')
				getProducts(mcls, path)


def getProducts(cls, path):

	while True:
		print('query {}, url:{}'.format(cls, BASE_URL+path))
		rsp = rq.get(BASE_URL+path)
		# product count are put in json structure, retrive it from "searchProductListModel" json object
		match = re.search(r'searchProductListModel\s+=(.*);', rsp.text)
		if(match and match.group(1)):
			j = json.loads(json.loads(match.group(1)))
			count = j['Count']

			for p in j['ProductListModel']:
				print(p['Name'])
				classesFile.write('{},{}\n'.format(cls, p['Name']))
				imagesFile.write('{},{}\n'.format(p['Name'], p['PictureUrl']))
			page = int(count/20)
			if(page %20 != 0):
				page +=1
			print('page count:%d'%page)

			chrome_options = webdriver.ChromeOptions()
			prefs = {"profile.default_content_setting_values.notifications" : 2}
			chrome_options.add_experimental_option("prefs",prefs)
			driver = webdriver.Chrome('/home/kevin/bin/chromedriver',chrome_options=chrome_options)
			driver.get(BASE_URL+path)
			time.sleep(3)

			p = 2
			while True:
				if(p >= page+1):
					break;
				print('page:{}'.format(p))
				try:
					next = driver.find_element_by_xpath('//li[@jp-role="next"]')
					next.click()
					# this could prevent search fail
					driver.execute_script("setTimeout(function() { hide() }, 100);")

					# scroll down to end of page
					for i in range(0,3):
						driver.execute_script("window.scrollTo(0, {});".format(1080*i))
						time.sleep(1)

					itemRead = 0

					'''
					<div class="box-img">
						<p class="stockup" style="display: none;">補貨中</p>
						<a href="/1472194300101?categoryId=71">
							<img onerror="nofind(this);" alt="家樂福枸杞-200g" data-src="https://image.azureedge.net/0231506_S.jpeg" src="https://image.azureedge.net/0231506_S.jpeg" class="m_lazyload" style="display: block;">
							<!---->
							<!---->
						</a>
					</div>
					'''

					for n in driver.find_elements_by_xpath('//div[@class="box-img"]/a/img'):
						name = n.get_attribute('alt').strip()
						classesFile.write('{},{}\n'.format(cls.strip(), name))
						imagesFile.write('{},{}\n'.format(name, n.get_attribute('src')))
						itemRead +=1
					if(itemRead == 0):
						print('read nothing here!!')
					p +=1
				except:
					print('Error! Can not locate next! try again!')
					time.sleep(5)
					driver.refresh()

			driver.close()
			break
		else:
			print('can not find searchProductListModel, try again!')
			time.sleep(5)

if not os.path.isdir('./data'):
	os.mkdir('./data')
classesFile = io.open('./data/carrefour_classes.csv','w')
imagesFile = io.open('./data/carrefour_images.csv','w')
start()
classesFile.close()
imagesFile.close()