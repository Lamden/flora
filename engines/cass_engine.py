import logging
from pkg_resources import resource_filename
from sqlalchemy import create_engine
from engine import Engine
import logging
import pickle
import uuid

from cassandra.cluster import Cluster
from cass_auth import KeyAuthProvider

class Casssandra_Engine(Engine):
	def __init__(self, *args):
		self.log = logging.getLogger(resource_filename(__name__, __file__))

		self.cluster = Cluster(args[0], port=args[1])
		self.pub = args[2]
		self.priv = args[3]

		# going to have to modify this shit later.
		self.connection = self.cluster.connect(auth_provider=KeyAuthProvider(None, None, None))

	def exists(self, query):
		if query == None:
			return False
		return True

	def check_name(self, name):
		query = self.connection.execute("SELECT * FROM names WHERE name='{}'".format(name)).fetchone()
		return self.exists(query)

	def add_name(self, name, n, e):
		query = self.connection.execute('INSERT INTO names (id, name, n, e) VALUES (?,?,?,?)', (uuid.uuid1(), name, n, e))
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
		query = self.connection.execute("SELECT * FROM packages WHERE owner='{}' AND package='{}' ALLOW FILTERING".format(owner, package)).fetchone()
		return self.exists(query)

	def get_key(self, name):
		return self.connection.execute("SELECT n, e FROM names WHERE name='{}'".format(name)).fetchone()

	def add_package(self, owner, package, template, example):
		self.connection = self.cluster.connect(auth_provider=KeyAuthProvider(owner, self.pub, self.priv))

		self.connection.execute('INSERT INTO packages VALUES (?,?,?,?)', (owner, package, template, example))
		return self.check_package(owner, package)
