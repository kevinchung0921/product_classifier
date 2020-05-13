# coding = utf-8
import os
import io
import re
import json
from tqdm import tqdm


def writeDataSet(pattern):

	classDict = json.loads(io.open('./data/dict_simple.json').read())
	count = 0
	for fn in os.listdir('./data'):
		# go through every file with "yahoo" prefix txt file
		if(re.match(pattern,fn)):
			fp = io.open('./data/'+fn)
			print('reading %s'%fn)
			for line in tqdm(fp.readlines()):

				# every line should contains csv separator ","
				if(line.find(',') < 0):
					print('can not find "," in line %s'%line)
					continue

				array = line.split(',')
				cls = array[0]
				if(cls not in classDict):
					continue

				# 	classDict[cls] = len(classDict.keys())+1
				name = ' '.join(array[1:])

				# insert space for each chinese character
				name = re.sub(r'([\u4e00-\u9fff])',r' \1 ',name)

				# name = re.sub(r'【.+】','',name)
				# name = re.sub(r'\(.+\)','',name)
				# name = re.sub(r'\[.+\]','',name)
				# name = re.sub(r'『.+』','',name)

				# do not add empty string, otherwise will cause exception in training
				if(name == None or name == '' or name.strip() == '' or name in nameSet):
					continue

				nameSet.add(name)
				data = "{} , {}".format(classDict[cls], name)

				# use 1/10 data for test
				if(count % 10 == 0):
					test.write(data)
				else:
					train.write(data)
				count += 1



def convertCsvToDict():
	# format:  class name, class group, class number
	with io.open('./data/classes_34.csv','r') as f:

		clsdict = {}
		for line in f.readlines():
			a = line.split(",")
			cls = a[0]
			if(a[2] != "\n" and a[2] != None):
				idx = int(a[2])
				if(cls not in clsdict):
					clsdict[cls] = idx
				elif (clsdict[cls] != idx):
					print('error %s exist with idx:%d, new idx is %d'%(cls, clsdict[cls], idx))

		with io.open('./data/dict_simple.json','w') as out:
			out.write(json.dumps(clsdict, indent=4, ensure_ascii=False))
			out.close()

def showClasses(pattern):
	classSet = set()
	for fn in os.listdir('./data'):
		if(re.match(pattern,fn)):
			fp = io.open('./data/'+fn)
			for line in tqdm(fp.readlines()):
				array = line.split(',')
				cls = array[0]
				classSet.add(cls)
	for s in classSet:
		print(s)

convertCsvToDict()
# create a set to prevent duplicate name added
nameSet = set()

# open train and test file for append data
train = io.open('./data/train.csv','w+')
test = io.open('./data/test.csv','w+')

# read data
writeDataSet('yahoo_classes\d+.csv')
writeDataSet('costco_classes.csv')
writeDataSet('rt_classes.csv')
writeDataSet('carrefour_classes.csv')


train.close()
test.close()
