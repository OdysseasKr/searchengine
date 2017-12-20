from pymongo import MongoClient
import os

HOST = 'localhost'
PORT = 27017
DATABASE_NAME = 'testdb'

class CollectionIndexer:
	""" API for the list of all available collections
	"""
	def __init__(self, folder):
		"""
		Parameters
		----------
		folder: [String] root folder of all collections
		"""
		self._connection = MongoClient(HOST, PORT)
		self._database = self._connection['testdb']
		self._collection = self._database['all_collections']
		self._folder = folder

	def addCurrentFolders(self):
		""" Adds to the list all of the collections in the root folder
		"""
		collections = os.walk(self._folder).next()[1]
		for c in collections:
			self._collection.insert_one({
				'name': str(c),
				'size': len(os.listdir(os.path.join(self._folder,c)))
			})

	def addCollection(self, name):
		""" Adds a new collection to the list
		Parameters
		----------
		name: [String] name of the collection
		"""
		self._collection.insert_one({
			'name': name,
			'size': len(os.listdir(os.path.join(self._folder,name)))
		})

	def getCollectionSize(self, name):
		""" Returns the size of the given collection
		"""
		return self._collection.find_one({'name': word})['size']

	def empty(self):
		""" Deletes the index of collections
		"""
		self._collection.drop()

	@property
	def list(self):
		""" Returns a list of all collection names
		"""
		res_list = list(self._collection.find({},{'name':1, '_id':0}))
		return map((lambda x: x['name']), res_list)
