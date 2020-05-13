import torch
import torchtext
from torchtext.datasets import text_classification
import os
import torch.nn as nn
import torch.nn.functional as functional
from torch.utils.data import DataLoader
import time
from torch.utils.data.dataset import random_split

from torchtext.data.utils import ngrams_iterator, get_tokenizer
from torchtext.vocab import build_vocab_from_iterator, Vocab
from torchtext.datasets.text_classification import _csv_iterator, _create_data_from_iterator, TextClassificationDataset

NGRAMS = 2
BATCH_SIZE = 16
EMBED_DIM = 32
N_EPOCHS = 5

device = torch.device('cuda' if torch.cuda.is_available() else "cpu")


def loadData(train_csv_path, test_csv_path, ngrams):
	vocab = build_vocab_from_iterator(_csv_iterator(train_csv_path, ngrams))

	train_data, train_labels = _create_data_from_iterator(
		vocab, _csv_iterator(train_csv_path, ngrams, yield_cls=True), False)
	test_data, test_labels =_create_data_from_iterator(
		vocab, _csv_iterator(test_csv_path, ngrams, yield_cls=True), False)

	return (TextClassificationDataset(vocab, train_data, train_labels),
		TextClassificationDataset(vocab, test_data, test_labels))


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


# dump string to index mapping which required for testing
def dumpVocab(vocab):
	import json
	import io
	f = io.open('stoi.json','w')
	f.write(json.dumps(vocab.stoi,ensure_ascii=False))
	f.close()


def generate_batch(batch):
	label = torch.tensor([entry[0] for entry in batch])
	text = [entry[1] for entry in batch]
	offsets = [0] + [len(entry) for entry in text]

	offsets = torch.tensor(offsets[:-1]).cumsum(dim=0)
	text = torch.cat(text)
	return text, offsets, label



def train_func(sub_train_):
	train_loss = 0
	train_acc = 0
	data = DataLoader(sub_train_, batch_size=BATCH_SIZE, shuffle=True, collate_fn=generate_batch)
	for i, (text, offsets, cls) in enumerate(data):
		optimizer.zero_grad()
		text, offsets, cls = text.to(device), offsets.to(device), cls.to(device)
		output = model(text, offsets)
		loss = criterion(output, cls)
		train_loss += loss.item()
		loss.backward()
		optimizer.step()
		train_acc += (output.argmax(1) == cls).sum().item()

	scheduler.step()

	return train_loss / len(sub_train_), train_acc / len(sub_train_)

def test(data_):
	loss = 0
	acc = 0
	data = DataLoader(data_, batch_size = BATCH_SIZE, collate_fn = generate_batch)
	for text, offsets, cls in data:
		text, offsets, cls = text.to(device), offsets.to(device), cls.to(device)
		with torch.no_grad():
			output = model(text, offsets)
			loss = criterion(output, cls)
			loss += loss.item()
			acc += (output.argmax(1) == cls).sum().item()

	return loss / len(data_), acc/len(data_)


train_dataset, test_dataset = loadData('./train.csv','./test.csv', NGRAMS)

dumpVocab(train_dataset.get_vocab())

NUM_CLASS = len(train_dataset.get_labels())
print('class:{}'.format(NUM_CLASS))

VOCAB_SIZE = len(train_dataset.get_vocab())
print('vocab size:{}'.format(VOCAB_SIZE))

model = TextSentiment(VOCAB_SIZE, EMBED_DIM, NUM_CLASS).to(device)

min_valid_loss = float('inf')

criterion = torch.nn.CrossEntropyLoss().to(device)
optimizer = torch.optim.SGD(model.parameters(), lr=4.0)
scheduler = torch.optim.lr_scheduler.StepLR(optimizer, 1, gamma=0.7)

train_len = int(len(train_dataset) * 0.9)
sub_train_, sub_valid_ = random_split(train_dataset, [train_len, len(train_dataset) - train_len])

for epoch in range(N_EPOCHS):

	start_time = time.time()
	train_loss, train_acc = train_func(sub_train_)
	valid_loss, valid_acc = test(sub_valid_)

	secs = int(time.time() - start_time)
	mins = secs/60
	secs = secs%60

	print('Epoch: %d' %(epoch + 1), " | time in %d minutes, %d seconds" %(mins, secs))
	print('\tLoss: %f(train)\t|\tAcc: %f%%(train)'%(train_loss, train_acc*100))
	print('\tLoss: %f(valid)\t|\tAcc: %f%%(valid)'%(valid_loss, valid_acc*100))

torch.save(model, 'product_classifier_1.pt')

print('Checking the results of test dataset...')
test_loss, test_acc = test(test_dataset)
print('\tLoss: %f (test)\t|\tAcc: %f %%(test)'%(test_loss, (test_acc * 100)))

