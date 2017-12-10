import numpy as np
from pymongo import MongoClient

HOST = 'localhost'
PORT = 27017
DATABASE_NAME = 'testdb'

class InvertedIndexRAM:
	def __init__(self):
		self._index = {}

	def add(self, words, document, weights)
		for word, weight in zip(words,weights):
			self.addOne(word, document, weight)

	def addOne(self, word, document):
		if word not in self._index:
			self._index[word] = [document]
		else:
			self._index[word].append(document)

	def getDocumentsByWord(self, word):
		if word not in self._index:
			return [];
		return self._index[word]

	def getCorpus(self):
		return self._index.keys()

class InvertedIndexDB:
	def __init__(self, collection_name):
		self._connection = MongoClient(HOST, PORT)
		self._database = self._connection[DATABASE_NAME]
		self._collection_name = collection_name

		self._collection = self._database[self._collection_name]

	def add(self, words, document, weights):
		for word, weight in zip(words,weights):
			self.addOne(word, document, weight)

	def addOne(self, word, document, weight):
		# Maybe this can be optimized
		if self._collection.find_one({"word": word}):
			self._collection.update_one(
				{"word": word},
				{'$push': {'docs': {
					"docname": document,
					"weight": weight
				}}}
			)
		else:
			self._collection.insert_one({
				"word": word,
				"docs": [{
					"docname": document,
					"weight": weight
				}]
			})

	def getDocumentsByWord(self, word):
		item = self._collection.find_one({"word": word})
		if item:
			return list(map((lambda x: x['docname']), item['docs']))
		else:
			return []

	def getCorpus(self):
		res_list = list(self._collection.find({},{"word":1, "_id":0}))
		return list(map((lambda x: x['word']), res_list))
