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

		self.cluster = Cluster(args[0])

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
		results = self.connection.execute(prepared, arguments)
		return results.current_rows

	def exists(self, query):
		if len(query) <= 0:
			return False
		return True

	def check_name(self, name):
		return self.exists(self.prepare_execute_return("SELECT * FROM public.users \
			where name=?", (name,)))

	def add_name(self, name, n, e):
		self.prepare_execute_return("INSERT INTO public.users (name, n, e) \
			VALUES (?, ?, ?) IF NOT EXISTS", (name, n, e))
		return self.check_name(name)

	def get_package(self, owner, package):
		query = "SELECT template, example FROM public.contracts \
			WHERE owner=? AND package=? ALLOW FILTERING"
		fetched = self.prepare_execute_return(query, (owner, package))

		if not self.exists(fetched):
			return False

		return {
			'template' : str(pickle.loads(fetched[0][0])),
			'example' : str(pickle.loads(fetched[0][1]))
		}

	def check_package(self, owner, package):
		return self.exists(self.prepare_execute_return("SELECT * FROM public.contracts \
			WHERE owner=? AND package=? ALLOW FILTERING", (owner, package)))

	def get_key(self, name):
		return self.prepare_execute_return("SELECT n, e FROM public.users where name = ?", (name,))[0]

	def add_package(self, owner, package, template, example):
		self.prepare_execute_return("INSERT INTO public.contracts (id, owner, package, template, example) \
			VALUES (?, ?, ?, ?, ?) IF NOT EXISTS", (uuid.uuid1(), owner, package, template, example))
		return self.check_package(owner, package)

	def set_secret(self, name, secret):
		self.prepare_execute_return("UPDATE public.users SET secret=? where name=?", (secret, name))
		return self.exists(self.get_named_secret(name))

	def get_named_secret(self, name):
		return self.prepare_execute_return("SELECT secret FROM public.users where name = ?", (name,))[0][0]
