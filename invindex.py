import numpy as np
from pymongo import MongoClient

HOST = 'localhost'
PORT = 27017
DATABASE_NAME = 'testdb'

class InvertedIndexRAM:
	def __init__(self):
		self._index = {}
		self._docs = set()

	def add(self, words, document):
		for word, weight in words:
			self.addOne(word, weight, document)

	def addOne(self, word, weight, document):
		if word not in self._index:
			self._index[word] = [(document,weight)]
		else:
			self._index[word].append((document,weight))
		self._docs.add(document)

	def getDocumentsByWord(self, word):
		if word not in self._index:
			return [];
		return self._index[word]

	@property
	def corpus(self):
		return set(self._index.keys())

	@property
	def documents(self):
		return self._docs


class InvertedIndexDB:
	def __init__(self, collection_name):
		self._connection = MongoClient(HOST, PORT)
		self._database = self._connection[DATABASE_NAME]
		self._collection_name = collection_name

		self._collection = self._database[self._collection_name]
		self._doc_collection = self._database[self._collection_name+"DOCS"]

	def add(self, words, document):
		for word, weight in words:
			self.addOne(word, weight, document)

	def addOne(self, word, weight, document):
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

		if not self._doc_collection.find_one({"name": document}):
			self._doc_collection.insert_one({"name": document})

	def getDocumentsByWord(self, word):
		item = self._collection.find_one({"word": word})
		if item:
			return list(map((lambda x: (x['docname'], x['weight'])), item['docs']))
		else:
			return []

	@property
	def corpus(self):
		res_list = list(self._collection.find({},{"word":1, "_id":0}))
		return set(map((lambda x: x['word']), res_list))

	@property
	def documents(self):
		res_list = list(self._doc_collection.find({},{"name":1, "_id":0}))
		return set(map((lambda x: x['name']), res_list))
