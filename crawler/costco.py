import requests as rq
from bs4 import BeautifulSoup
import io
import os
import time
import re
from selenium import webdriver

BASE_URL = "https://www.costco.com.tw/"



def writeToFile(cls, soup):
	'''
		<div class="product-image ">
            <a class="thumb" href="/Electronics/Audio-Video/Speakers-Soundbars-Home-Theater/Bose-Home-Theater-System-SoundTouch-300/p/1141972" title="Bose 兩件式家庭劇院組 SoundTouch 300" role="link">
                <img src="/medias/sys_master/images/hf3/h43/10720153632798.jpg" alt="Bose 兩件式家庭劇院組 SoundTouch 300" title="Bose 兩件式家庭劇院組 SoundTouch 300">
			</a>
            <img class="decal-position-1" src="/mediapermalink/decal_onlineExclusive" alt="null">
		</div>
	'''

	for img in soup.select('div.product-image > a > img'):
		name = img.get('title').strip()
		classesFile.write('{}, {}\n'.format(cls, name))
		url = img.get('src')
		imagesFile.write('{}, {}\n'.format(name, 'https://costco.com.tw'+url))

def getPages(soup):
	'''
		<div class="search-pagination-container hidden-xs">
			<span>顯示</span> 1 - 28<span> 之</span> 28
		</div>
	'''
	# get total number
	div = soup.find('div',{'class':'search-pagination-container hidden-xs'})

	if(div == None):
		return

	match = re.search(r'之 (\d+)',div.text)

	totalCount = 0

	if(match != None):
		totalCount = int(match.group(1))
	else:
		# try english version, sometimes it change to english version
		match = re.search(r'of (\d+)',div.text)
		if(match != None):
			totalCount = int(match.group(1))

	print('product count:%d'%totalCount)
	pages = int(totalCount / 100)

	if(totalCount % 100 != 0):
		pages += 1
	print('page count:%d'%pages)
	return pages

def getProducts(url, cls):

	print('[{}] {}'.format(cls, url))
	rsp = rq.get(url)

	soup = BeautifulSoup(rsp.text, 'lxml')

	pages = getPages(soup)

	if(pages == None):
		return

	# get first page
	writeToFile(cls, soup)

	# go to other page
	for p in range(1, pages):
		print('page:%d'%p)
		rsp = rq.get(url+"?q=%3Aprice-desc&page={}".format(p))
		writeToFile(cls,BeautifulSoup(rsp.text, 'lxml'))


def start():
	rsp = rq.get(BASE_URL)
	soup = BeautifulSoup(rsp.text, 'lxml')

	for top in soup.findAll('li',{'class':'topmenu'}):
		if(top == None):
			print('can not find top menu')
			break
		for a in top.findAll('a', {'class':'show-sub-menu hidden-xs hidden-sm'}):
			getProducts(BASE_URL+a.get('href'), a.text.strip())


if not os.path.isdir('./data'):
	os.mkdir('./data')
classesFile = io.open('./data/costco_classes.csv','w')
imagesFile = io.open('./data/costco_images.csv','w')
start()
classesFile.close()
imagesFile.close()