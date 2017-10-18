import logging
from pkg_resources import resource_filename
from sqlalchemy import create_engine
from engine import Engine
import logging
import pickle
import uuid

from cassandra.cluster import Cluster

class Cassandra_Engine(Engine):
	def __init__(self, *args):
		self.log = logging.getLogger(resource_filename(__name__, __file__))

		self.cluster = Cluster(args[0])#, port=args[1])
		# self.pub = args[2]
		# self.priv = args[3]

		# going to have to modify this shit later.
		self.connection = self.cluster.connect()

		self.connection.execute("CREATE KEYSPACE IF NOT EXISTS public \
			WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };")

		self.connection.execute("CREATE TABLE IF NOT EXISTS public.users ( \
			name text PRIMARY KEY, \
			n text, \
			e text);")

		self.connection.execute("CREATE TABLE IF NOT EXISTS public.contracts ( \
			id uuid PRIMARY KEY, \
			owner text, \
			package text, \
			template blob, \
			example blob);")

	def exists(self, query):
		if len(query) <= 0:
			return False
		return True

	def check_name(self, name):
		results = self.connection.execute("SELECT * FROM public.users \
			where name = '{}'".format(name))
		fetched = results.current_rows
		return self.exists(fetched)

	def add_name(self, name, n, e):
		self.connection.execute("INSERT INTO public.users (name, n, e) \
			VALUES ('{}', '{}', '{}') IF NOT EXISTS".format(name, n, e))
		return self.check_name(name)

	def get_package(self, owner, package):
		results = self.connection.execute("SELECT * FROM public.contracts \
			WHERE owner='{}' AND package='{}' ALLOW FILTERING".format(owner, package))
		fetched = results.current_rows
		print(fetched)

		if not self.exists(fetched):
			print('ree')
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
		self.connection = self.cluster.connect()

		self.connection.execute('INSERT INTO packages VALUES (?,?,?,?)', (owner, package, template, example))
		return self.check_package(owner, package)
