#!/usr/bin/python3
from flask import Flask, request
import io
import json
import sys
import torch
import torch.nn as nn
import time
import re
import traceback
from torchtext.data import utils
from torchtext.data.utils import _basic_english_normalize

device = torch.device('cuda' if torch.cuda.is_available() else "cpu")

# Model declaration
class TextSentiment(nn.Module):
	def __init__(self, vocab_size, embed_dim, num_class):
		super().__init__()
		self.embedding = nn.EmbeddingBag(vocab_size, embed_dim, sparse=True)
		self.fc = nn.Linear(embed_dim, num_class)
		self.init_weights()

	def init_weights(self):
		initrange = 0.5
		self.embedding.weight.data.uniform_(-initrange, initrange)
		self.fc.weight.data.uniform_(-initrange, initrange)
		self.fc.bias.data.zero_()

	def forward(self, text, offsets):
		embedded = self.embedding(text, offsets)
		return self.fc(embedded)


# load parameters
model = torch.load('./product_classifier_1.pt')
model.eval()

# just for eaier reading
class_dict = json.loads(io.open('./dict_simple.json').read())
class_idx_to_name = {}
for k in class_dict.keys():
	class_idx_to_name[class_dict[k]] = k


stoi = json.loads(io.open('./stoi.json').read())

def classify(text):
	print('predicting ['+text+']')

	# normalize input string
	text = re.sub(r'([\u4e00-\u9fff])',r' \1',text)
	l = list(utils.ngrams_iterator(_basic_english_normalize(text),2))
	l = [[stoi.get(token, 0) for token in l]]

	text = torch.tensor(l)

	with torch.no_grad():
		result = model(text, None)

		# sort result according score
		value, index = (torch.sort(result,descending=True))
		classIdx = []
		scores = []

		print("===========================================")
		# just pick 3 most relevant class
		for i in range(0,3):
			idx = index[0][i].item()+1
			score = value[0][i].item()
			print("class:{}, score:{}".format(class_idx_to_name[idx], score))
			classIdx.append(idx)
			scores.append(int(score))
		return classIdx, scores



app = Flask(__name__)

@app.route("/product_class", methods=['GET'])
def getProduct():
	result = {}
	try:
		product = request.args.get('product')
		if(product != None and len(product) >= 2):
			classIdx, scores = classify(product)
			result['class'] = classIdx[0]
			result['score'] = scores[0]
			result['version'] = 1
	except:
		traceback.print_exc()
	return result

@app.route("/product_class", methods=['POST'])
def postProducts():
	startTime = time.time()
	results = []
	try:
		jdata = request.data
		products = json.loads(jdata)['products']
		print("list length:%d"%len(products))
		if(products != None):
			for product in products:
				r = product # copy content for send back
				r['class'], r['score'] = classify(product['name'])
				results.append(r)
	except:
		traceback.print_exc()
	print('query takes %f seconds'%(time.time()-startTime))
	return {'results':results, 'version':1}

app.run(debug=False, host='0.0.0.0', port=5000)
