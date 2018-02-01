from pymongo import MongoClient

HOST = 'localhost'
PORT = 27017
DATABASE_NAME = 'testdb'

class IndexCreator:
	""" Used to create an inverted index. It uses RAM until self.LIMIT is reached.
	Then stores everything in the mongo database, emptys RAM and continue creating in RAM.
	Remember to call close when finished.
	"""
	def __init__(self, collection_name):
		"""
		Parameters
		----------
		collection_name: [String] the name of the collection to access
		"""
		self._counter = 0
		self.LIMIT = 10**10
		self._collection_name = collection_name

		self._index = {}
		self._docs = {}

		self._connection = MongoClient(HOST, PORT)
		self._database = self._connection[DATABASE_NAME]
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
			self._addOne(w, words[w], document)

		self._docs[document] = {"name": document, "title": "", "desc": ""}

		self._counter += (len(words))
		if self._counter >= self.LIMIT:
			self._store()

	def _addOne(self, word, weight, document):
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

	def setDocumentProperties(self, document, title, description, max_f):
		""" Sets the document properties
		Parameters
		----------
		document: document name
		title: document title
		description: short excerpt from document
		"""
		self._docs[document] = {
			"name": document,
			"title": title,
			"desc": description,
			"max": max_f
		}

	def _store_word(self, word, values):
		""" Stores an occurency list of a specific word to the mongo db
		Parameters
		----------
		word: the word to be associated with the given list
		values: the occurency list
		"""
		formatted_values = list(map(lambda x: {"docname":x[0], "weight": x[1]}, values))
		if self._collection.find_one({"word": word}):
			self._collection.update_one(
				{"word": word},
				{'$push': {'docs': {
					'$each': values
				}}}
			)
		else:
			self._collection.insert_one({
				"word": word,
				"docs": formatted_values
		})

	def store(self):
		""" Stores the whole index in the database and empties RAM
		"""
		for word in self._index.keys():
			self._store_word(word, self._index[word])

		self._doc_collection.insert_many(self._docs.values())
		self.docs = {}
		self.index = {}
		self._counter = 0;

	def close(self):
		""" Stores the remaining of the index that resides in RAM, to the mongo db
		"""
		self.store()

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
		self._doc_collection.insert_one({"name": document})

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

	def getDocumentsByWord(self, word):
		"""  Returns the documents associated with the given word
		"""
		item = self._collection.find_one({"word": word})
		if item:
			return list(map((lambda x: (x['docname'], x['weight'])), item['docs']))
		else:
			return []

	def getWordsByDocument(self, doc):
		"""  Returns the documents associated with the given word
		"""
		items = self._collection.find({"docs.docname":doc},
									{ "word": 1, "docs.$": 1 })
		result = {w['word']: w['docs'][0]['weight'] for w in items}
		return result

	def setDocumentProperties(self, document, title, description, max_f):
		if self._doc_collection.find_one({"name": document}):
			self._doc_collection.update_one(
				{"name": document},
				{"$set": {
					"title": title,
					"desc": description,
					"max": max_f
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
