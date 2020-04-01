from pymongo import MongoClient


class cmongo(object):

	def __init__(self, db, collection):

		self.__client = MongoClient('localhost', 27017)
		self.__db = self.__client[db]
		self.__collection = self.__db[collection]

	@property
	def collection(self):
		return self.__collection


	