import requests as rq
from bs4 import BeautifulSoup
import io
import os
import time
import re

BASE_URL = 'https://www.rt-mart.com.tw/direct/'

def writeToFile(cls, soup):
	'''
	<div class="indexProList">
    	<div class="for_imgbox">
    		<a href="https://www.rt-mart.com.tw/direct/index.php?action=product_detail&amp;prod_no=P0000200786019">
    		<img src="https://www.rt-mart.com.tw/website/uploads_product/website_2/P0000200786019_2_1383366.jpg" width="140" height="140" border="0" title="宏都拉斯單一產區有機阿拉比卡豆" alt="宏都拉斯單一產區有機阿拉比卡豆"></a></div>
    	<h6 class="for_subname"></h6>
    	<h5 class="for_proname"><a href="https://www.rt-mart.com.tw/direct/index.php?action=product_detail&amp;prod_no=P0000200786019"> 宏都拉斯單一產區有機阿拉比卡豆</a></h5>
    	<div class="for_pricebox">
    		<div><span>$</span>190</div>
    	</div>
    </div>
	'''
	for a in soup.select('div.for_imgbox > a > img'):
		classesFile.write("{}, {}\n".format(cls, a.get('title')))
		imagesFile.write("{}, {}\n".format(a.get('title'), a.get('src')))


def getPages(soup):
	# get product count for calculate pages
	itemCounts = int(soup.find('span',{'class':'t02'}).text)
	print('product counts:%d'%(itemCounts))

	# 18 products per page
	pages = int(itemCounts/18)

	# extra page if has remainders
	if(itemCounts%18 != 0):
		pages+=1

	return pages

def getProducts(classNumber):

	link = BASE_URL + 'index.php?action=product_sort&prod_sort_uid={}'.format(classNumber)
	rsp = rq.get(link)
	soup = BeautifulSoup(rsp.text, "lxml")

	# get class name
	cls = soup.find('span',{'class':'t01'}).text

	pages = getPages(soup)

	writeToFile(cls, soup)

	# reading other pages if have
	for page in range(2, pages+1):
		print('reading page:%d'%page)
		pageLink = link+'&prod_size=&p_data_num=18&usort=auto_date%%2CDESC&page={}'.format(page)
		rsp = rq.get(pageLink)
		writeToFile(cls, BeautifulSoup(rsp.text, "lxml"))



def start():
	rsp = rq.get(BASE_URL)
	soup = BeautifulSoup(rsp.text, 'lxml')
	for li in soup.findAll('li', {'class':['nav01','nav02']}):
		for h4 in li.findAll('h4'):
			a = h4.find('a',href=True)
			url = a.get('href')
			match = re.search(r'prod_sort_uid=(\d+)', url)
			if(match and match.group(1)):
				getProducts(match.group(1))


if not os.path.isdir('./data'):
	os.mkdir('./data')
# file for class -> name
classesFile = io.open('./data/rt_classes.csv','w')
# file for name  -> image url
imagesFile = io.open('./data/rt_images.csv','w')
start()
classesFile.close()
imagesFile.close()


