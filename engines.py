import ipfsapi
from sqlalchemy import create_engine
import json
import os

class Engine:
	def __init__(self, *args):
		raise NotImplementedError()
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
	def get_secret(self, name):
		raise NotImplementedError()
	def add_package(self, owner, package, template, example):
		raise NotImplementedError()

class IPFS_Engine(Engine):
	def __init__(self, *args):
		# info = ('127.0.0.1', 5000)
		# (IP add str, port int)
		try:
			self.api = ipfsapi.connect(args[0], args[1])
			self.root_hash = args[2]
			self.root_dir = args[3]
		except:
			raise Exception('Daemon not running')

		self.add_dir(os.path.join(os.getcwd(), self.root_dir))

	def add_dir(self, path):
		try:
			hashes = self.api.add(path, recursive=True)
			end_hash = hashes[-1]
			self.root_hash = end_hash['Hash']
			print(self.root_hash)
			return end_hash['Hash']
		except:
			# fails if nothing is in the directory
			return False

	def update_fs(self):
		try:
			self.add_dir(os.path.join(os.getcwd(), self.root_dir))
			return True
		except:
			return False

	def exists(self, query):
		if query == None:
			return False
		return True

	def check_name(self, name):
		try:
			query = self.api.ls('{}/packages/{}'.format(self.root_hash, name))
			return True
		except:
			return False

	def add_name(self, name, n, e):
		package_root = os.path.join(os.getcwd(), '{}/packages'.format(self.root_dir))
		package_path = (os.path.join(package_root, name))
		try:
			os.makedirs(package_path)
		except:
			pass

		name_root = os.path.join(os.getcwd(), '{}/names'.format(self.root_dir))
		name_path = (os.path.join(name_root, name))
		try:
			os.makedirs(name_path)
		except:
			pass

		with open(os.path.join(name_path, 'n'), 'w') as n_file:
			n_file.write(n)

		with open(os.path.join(name_path, 'e'), 'w') as e_file:
			e_file.write(e)

		self.update_fs()
		return self.check_name(name)

	def file_to_memory(self, path):
		data = None
		with open(path, 'r') as d:
			data = d.read()
		os.remove(path)
		return data

	def get_package(self, owner, package):
		# this will download locally or wherever the user is
		try:
			# pull it down from ipfs
			self.api.get('{}/packages/{}/{}'.format(self.root_hash, owner, package))

			# stores in cwdir, so load the files into memory and delete them
			template = self.file_to_memory('{}/{}/template'.format(os.getcwd(), package))
			example = self.file_to_memory('{}/{}/example'.format(os.getcwd(), package))
			os.rmdir('{}/{}'.format(os.getcwd(), package))

			return {
				'template' : template,
				'example' : example
			}
		except:
			return False

	def check_package(self, owner, package):
		try:
			query = self.api.ls('{}/packages/{}/{}'.format(self.root_hash, owner, package))
			return True
		except:
			return False
	
	def get_key(self, name):
		try:
		# pull it down from ipfs
			self.api.get('{}/names/{}'.format(self.root_hash, name))

			# stores in cwdir, so load the files into memory and delete them
			n = self.file_to_memory('{}/{}/n'.format(os.getcwd(), name))
			e = self.file_to_memory('{}/{}/e'.format(os.getcwd(), name))

			os.rmdir('{}/{}'.format(os.getcwd(), name))

			return (n, e)
		except:
			return False
	
	def set_secret(self, name, secret):
		if self.check_name(name):
			try:
				name_root = os.path.join(os.getcwd(), '{}/names'.format(self.root_dir))
				name_path = (os.path.join(name_root, name))

				with open(os.path.join(name_path, 'secret'), 'w') as secret_file:
					secret_file.write(secret)

				self.update_fs()
				return True
			except:
				return False
		return False
	
	def get_secret(self, name):
		try:
		# pull it down from ipfs
			self.api.get('{}/names/{}'.format(self.root_hash, name))

			# stores in cwdir, so load the files into memory and delete them
			secret = self.file_to_memory('{}/{}/secret'.format(os.getcwd(), name))

			os.rmdir('{}/{}'.format(os.getcwd(), name))

			return secret
		except:
			return False
	
	def add_package(self, owner, package, template, example):
		raise NotImplementedError()

class SQL_Engine(Engine):
	def __init__(self, *args):
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
			'template' : pickle.loads(query[0]),
			'example' : pickle.loads(query[1])
		}

	def check_package(self, owner, package):
		query = self.connection.execute("SELECT * FROM packages WHERE owner='{}' AND package='{}'".format(owner, package)).fetchone()
		return self.exists(query)

	def get_key(self, name):
		return self.connection.execute("SELECT n, e FROM names WHERE name='{}'".format(name)).fetchone()

	def set_secret(self, name, secret):
		self.connection.execute("UPDATE names SET secret=? WHERE name=?", (secret, name))
		return self.exists(query)

	def get_secret(self, name):
		return self.connection("SELECT secret FROM names WHERE name='{}'".format(name)).fetchone()

	def add_package(self, owner, package, template, example):
		self.connection.execute('INSERT INTO packages VALUES (?,?,?,?)', (owner, package, template, example))
		return self.check_package(owner, package)