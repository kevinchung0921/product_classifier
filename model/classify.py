# encoding = utf-8
import io
import json
import sys
import torch
import torch.nn as nn
import time
import re
from torchtext.data import utils
from torchtext.data.utils import _basic_english_normalize

device = torch.device('cuda' if torch.cuda.is_available() else "cpu")

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



model = torch.load('./product_classifier_1.pt')
model.eval()

class_dict = json.loads(io.open('./dict_simple.json').read())
class_idx_to_name = {}
for k in class_dict.keys():
	class_idx_to_name[class_dict[k]] = k


stoi = json.loads(io.open('./stoi.json').read())


def classify(text):
	text = re.sub(r'([\u4e00-\u9fff])',r' \1',text)
	l = list(utils.ngrams_iterator(_basic_english_normalize(text),2))
	l = [[stoi.get(token, 0) for token in l]]

	text = torch.tensor(l)

	with torch.no_grad():
		result = model(text, None)
		value, index = (torch.sort(result,descending=True))
		# print("===========================================")
		# for i in range(0,5):
		# 	classIdx = index[0][i].item()
		# 	score = value[0][i].item()
		# 	print("class:{}, score:{}".format(class_idx_to_name[classIdx+1], score))
		# print("===========================================")
		return index[0][0].item()+1

def commandLine():
	print('input string:')
	for line in sys.stdin:
		if(line == '\n'):
			print('input string:')
		else:
			idx = classify(line)
			print(" class:{} ".format(class_idx_to_name[idx]))

def autoTest():
	with io.open("./test.csv") as f:
		total = 0
		correct = 0
		errorCount = {}
		totalCount = {}
		for line in f.readlines():
			a = line.split(',')
			text = a[1]
			ans = int(a[0])
			idx = classify(text)
			if(idx == ans):
				correct += 1
			else:
				#print('{}, expect {} but return {}'.format(text.strip(), class_idx_to_name[ans], class_idx_to_name[idx]))
				if(ans not in errorCount):
					errorCount[ans] = 1
				else:
					errorCount[ans] += 1
			if(ans not in totalCount):
				totalCount[ans] = 1
			else:
				totalCount[ans] += 1
			total += 1
		for a in errorCount:
			print(" class:{} error count:{} error rate:{}".format(class_idx_to_name[a], errorCount[a], errorCount[a]/totalCount[a]))

		print("hit rate {}%".format((correct*100)/total))

#autoTest()
commandLine()