import requests as rq
from bs4 import BeautifulSoup
import io
import os
import time
import re
from selenium import webdriver

BASE_URL = "https://www.my9.com.tw/collections/"
TYPES = [

	"威士忌",
	"葡萄酒",
	"調烈酒",
	"中式白酒",
	"sake-清酒燒酎-純米酒",
	"香檳氣泡酒",
	"果實酒",
	"啤酒"
]

def scrollDown():
	for i in range(0, 5):
		driver.execute_script("window.scrollTo(0, {});".format(1080*i))
		time.sleep(0.2)

def getType(type):
	print('reading page: %s ...'%type)
	driver.get(BASE_URL+type)
	scrollDown()

	count = 1
	while True:
		driver.get(BASE_URL+type+"?page=%d"%count)
		time.sleep(1)
		scrollDown()
		for span in driver.find_elements_by_xpath('//span[@class="title"][@itemprop="name"]'):
			print(span.text)
			classesFile.write("酒, {}\n".format(span.text))

		count+=1
		next = driver.find_element_by_xpath('//div[@id="bc-sf-filter-load-more"]')
		if('display: none' in next.get_attribute('style')):
			print('reach the last page, start parsing..')
			break;






def start():
	rsp = rq.get(BASE_URL)
	soup = BeautifulSoup(rsp.text, 'lxml')

	for type in TYPES:
		getType(type)


if not os.path.isdir('./data'):
	os.mkdir('./data')
classesFile = io.open('./data/my9_classes.csv','w')
driver = webdriver.Chrome('/home/kevin/bin/chromedriver83')
start()
driver.close()
classesFile.close()