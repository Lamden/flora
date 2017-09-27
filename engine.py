import os
import json
import pickle
import engines

class Engine:
	def __init__(self, *args):
		super(engines.get(args[0]), self).__init__()
		self.log = logging.getLogger(resource_filename(__name__, __file__))

	def exists(self, query):
		raise NotImplementedError()

	def check_name(self, name):
		raise NotImplementedError()

	def add_name(self, name, n, e):
		raise NotImplementedError()

	def get_package(self, owner, package):
		raise NotImplementedError()

	def check_package(self, owner, package):
		raise NotImplementedError()

	def get_key(self, name):
		raise NotImplementedError()

	def set_secret(self, name, secret):
		raise NotImplementedError()

	def get_named_secret(self, name):
		raise NotImplementedError()

	def add_package(self, owner, package, template, example):
		raise NotImplementedError()
