import logging
from pkg_resources import resource_filename
from sqlalchemy import create_engine
from engine import Engine
import logging
import pickle
import uuid

from cassandra.cluster import Cluster
from cassandra.query import dict_factory, tuple_factory

class Cassandra_Engine(Engine):
	def __init__(self, *args):
		self.log = logging.getLogger(resource_filename(__name__, __file__))

		self.cluster = Cluster(args[0])#, port=args[1])
		# self.pub = args[2]
		# self.priv = args[3]

		# going to have to modify this shit later.
		self.connection = self.cluster.connect()
		self.connection.row_factory = tuple_factory
		self.connection.execute("CREATE KEYSPACE IF NOT EXISTS public \
			WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };")

		self.connection.execute("CREATE KEYSPACE IF NOT EXISTS internal \
			WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };")

		self.connection.execute("CREATE TABLE IF NOT EXISTS public.users ( \
			name text PRIMARY KEY, \
			n text, \
			e text, \
			secret text);")

		self.connection.execute("CREATE TABLE IF NOT EXISTS public.contracts ( \
			id uuid PRIMARY KEY, \
			owner text, \
			package text, \
			template blob, \
			example blob);")

	def prepare_execute_return(self, query, arguments):
		prepared = self.connection.prepare(query)
		#prepared = prepared.bind(arguments)
		results = self.connection.execute(prepared, arguments)
		return results.current_rows

	def exists(self, query):
		if len(query) <= 0:
			return False
		return True

	def check_name(self, name):
		query = "SELECT * FROM public.users \
			where name=?"
		fetched = self.prepare_execute_return(query, (name,))
		return self.exists(fetched)

	def add_name(self, name, n, e):
		query = "INSERT INTO public.users (name, n, e) \
			VALUES (?, ?, ?) IF NOT EXISTS"
		self.prepare_execute_return(query, (name, n, e))
		return self.check_name(name)

	def get_package(self, owner, package):
		query = "SELECT * FROM public.contracts \
			WHERE owner=? AND package=? ALLOW FILTERING"
		fetched = self.prepare_execute_return(query, (owner, package))

		if not self.exists(fetched):
			return False

		return {
			'template' : str(pickle.loads(query[0])),
			'example' : str(pickle.loads(query[1]))
		}

	def check_package(self, owner, package):
		query = "SELECT * FROM public.contracts \
			WHERE owner=? AND package=? ALLOW FILTERING"
		fetched = self.prepare_execute_return(query, (owner, package))
		return self.exists(fetched)

	def get_key(self, name):
		query = "SELECT n, e FROM public.users where name = ?"
		fetched = self.prepare_execute_return(query, (name,))
		return fetched[0]

	def add_package(self, owner, package, template, example):
		query = "INSERT INTO public.contracts (id, owner, package, template, example) \
			VALUES (?, ?, ?, ?, ?) IF NOT EXISTS"
		self.prepare_execute_return(query, (uuid.uuid1(), owner, package, template, example))
		return self.check_package(owner, package)

	def set_secret(self, name, secret):
		query = "UPDATE public.users SET secret=? where name=?"
		self.prepare_execute_return(query, (secret, name))
		return self.exists(self.get_named_secret(name))

	def get_named_secret(self, name):
		query = "SELECT secret FROM public.users where name = ?"
		fetched = self.prepare_execute_return(query, (name,))
		return fetched[0][0]
