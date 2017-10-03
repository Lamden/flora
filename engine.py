import os
import json
import pickle
import engines

class Engine:
	def __init__(self, *args):
		super(engines.get(args[0]), self).__init__()
		self.log = logging.getLogger(resource_filename(__name__, __file__))

	def exists(self, query):
		# returns True or False
		raise NotImplementedError()

	def check_name(self, name):
		# returns True or False
		raise NotImplementedError()

	def add_name(self, name, n, e):
		# returns True or False
		raise NotImplementedError()

	def get_package(self, owner, package):
		'''
		returns
		{
			'template' : str(pickle.loads(query[0])),
			'example' : str(pickle.loads(query[1]))
		}
		'''
		raise NotImplementedError()

	def check_package(self, owner, package):
		# returns True or False
		raise NotImplementedError()

	def get_key(self, name):
		raise NotImplementedError()

	def add_package(self, owner, package, template, example):
		raise NotImplementedError()

	def verify(self, message, name):
		pass
		#raise NotImplementedError()