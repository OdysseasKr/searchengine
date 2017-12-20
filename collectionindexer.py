from pymongo import MongoClient
import os

HOST = 'localhost'
PORT = 27017
DATABASE_NAME = 'testdb'

class CollectionIndexer:
	def __init__(self, folder):
		self._connection = MongoClient(HOST, PORT)
		self._database = self._connection['testdb']
		self._collection = self._database['all_collections']
		self._folder = folder

	def addCurrentFolders(self):
		collections = os.walk(self._folder).next()[1]
		for c in collections:
			self._collection.insert_one({
				'name': str(c),
				'size': len(os.listdir(os.path.join(self._folder,c)))
			})

	def addCollection(self, name):
		self._collection.insert_one({
			'name': name,
			'size': len(os.listdir(os.path.join(self._folder,name)))
		})

	def getCollectionSize(self, name):
		return self._collection.find_one({'name': word})['size']

	def empty(self):
		self._collection.drop()

	@property
	def list(self):
		res_list = list(self._collection.find({},{'name':1, '_id':0}))
		return set(map((lambda x: x['name']), res_list))

	@property
	def size(self):
		return len(self._collection.find())
