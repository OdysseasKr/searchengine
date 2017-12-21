from pymongo import MongoClient

HOST = 'localhost'
PORT = 27017
DATABASE_NAME = 'testdb'

class InvertedIndexRAM:
	""" Inverted index data structure stored in RAM
	"""
	def __init__(self):
		self._index = {}
		self._docs = set()

	def add(self, words, document):
		""" Adds the given document in association with the given word list
		Parameters
		----------
		words: Word list in the format
			[(word_string, weight_int),
			 (word_string, weight_int),
			 ...]
 		document: [String] filename of the document
		"""
		for w in words:
			self.addOne(w, words[w], document)

	def addOne(self, word, weight, document):
		""" Adds the given document in association with the given word and weight
		Parameters
		----------
		words: [String] the word contained in the document
		weight: [Integer] the number of occurences of the word in the document
		document: [String] filename of the document
		"""
		if word not in self._index:
			self._index[word] = [(document,weight)]
		else:
			self._index[word].append((document,weight))
		self._docs.add(document)

	def getDocumentsByWord(self, word):
		"""  Returns the documents associated with the given word
		"""
		if word not in self._index:
			return [];
		return self._index[word]

	@property
	def corpus(self):
		"""  A set of all words
		"""
		return set(self._index.keys())

	@property
	def documents(self):
		"""  A set of all filenames
		"""
		return self._docs


class InvertedIndexDB:
	""" Inverted index data structure stored in MongoDB
	"""
	def __init__(self, collection_name):
		"""
		Parameters
		----------
		collection_name: [String] the name of the collection to access
		"""
		self._connection = MongoClient(HOST, PORT)
		self._database = self._connection[DATABASE_NAME]
		self._collection_name = collection_name

		self._collection = self._database[self._collection_name]
		self._doc_collection = self._database[self._collection_name+"DOCS"]

	def add(self, words, document):
		""" Adds the given document in association with the given word list
		Parameters
		----------
		words: Word list in the format
			[(word_string, weight_int),
			 (word_string, weight_int),
			 ...]
 		document: [String] filename of the document
		"""
		for w in words:
			self.addOne(w, words[w], document)

	def addOne(self, word, weight, document):
		""" Adds the given document in association with the given word and weight
		Parameters
		----------
		words: [String] the word contained in the document
		weight: [Integer] the number of occurences of the word in the document
		document: [String] filename of the document
		"""

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
		"""  Returns the documents associated with the given word
		"""
		item = self._collection.find_one({"word": word})
		if item:
			return list(map((lambda x: (x['docname'], x['weight'])), item['docs']))
		else:
			return []

	def setDocumentProperties(self, document, title, description):
		if self._doc_collection.find_one({"name": document}):
			self._doc_collection.update_one(
				{"name": document},
				{"$set": {
					"title":title,
					"desc":description
				}}
			)

	def getDocumentProperties(self, document):
		return self._doc_collection.find_one({"name": document})

	@property
	def corpus(self):
		"""  A set of all words
		"""
		res_list = list(self._collection.find({},{"word":1, "_id":0}))
		return set(map((lambda x: x['word']), res_list))

	@property
	def documents(self):
		"""  A set of all filenames
		"""
		res_list = list(self._doc_collection.find({},{"name":1, "_id":0}))
		return set(map((lambda x: x['name']), res_list))
