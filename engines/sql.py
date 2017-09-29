import logging
from pkg_resources import resource_filename
from sqlalchemy import create_engine
from engine import Engine
import logging
import pickle

class SQL_Engine(Engine):
	def __init__(self, *args):
		self.log = logging.getLogger(resource_filename(__name__, __file__))
		self.engine = create_engine(args[0])
		self.connection = self.engine.connect()

	def exists(self, query):
		if query == None:
			return False
		return True

	def check_name(self, name):
		query = self.connection.execute("SELECT * FROM names WHERE name='{}'".format(name)).fetchone()
		return self.exists(query)

	def add_name(self, name, n, e):
		query = self.connection.execute('INSERT INTO names VALUES (?,?,?,?)', (name, n, e, ''))
		return self.check_name(name)

	def get_package(self, owner, package):
		query = self.connection.execute("SELECT template, example FROM packages WHERE owner=? AND package=?", (owner, package)).fetchone()

		if query == None:
			return False

		return {
			'template' : str(pickle.loads(query[0])),
			'example' : str(pickle.loads(query[1]))
		}

	def check_package(self, owner, package):
		query = self.connection.execute("SELECT * FROM packages WHERE owner='{}' AND package='{}'".format(owner, package)).fetchone()
		return self.exists(query)

	def get_key(self, name):
		return self.connection.execute("SELECT n, e FROM names WHERE name='{}'".format(name)).fetchone()

	def set_secret(self, name, secret):
		self.connection.execute("UPDATE names SET secret=? WHERE name=?", (secret, name))
		return self.exists(self.get_named_secret(name))

	def get_named_secret(self, name):
		return self.connection.execute("SELECT secret FROM names WHERE name='{}'".format(name)).fetchone()[0]

	def add_package(self, owner, package, template, example):
		self.connection.execute('INSERT INTO packages VALUES (?,?,?,?)', (owner, package, template, example))
		return self.check_package(owner, package)
