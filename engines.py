import ipfsapi
from sqlalchemy import create_engine
import json
import os
import pickle

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

		self.sync(os.path.join(os.getcwd(), self.root_dir))

	# helper funcs
	def update_fs(self):
		try:
			self.sync(os.path.join(os.getcwd(), self.root_dir))
			return True
		except:
			return False

	def new_file(self, path, payload):
		try:
			with open(path, 'w') as f:
				f.write(payload)
			return True
		except:
			return False

	def new_dir(self, path):
		try:
			os.makedirs(path)
			return True
		except:
			return False

	def sync(self, path):
		try:
			hashes = self.api.add(path, recursive=True)
			end_hash = hashes[-1]
			self.root_hash = end_hash['Hash']
			print(self.root_hash)
			return end_hash['Hash']
		except:
			# fails if nothing is in the directory
			return False

	def file_to_memory(self, path):
		data = None
		with open(path, 'r') as d:
			data = d.read()
		os.remove(path)
		return data

	# wtf is this shit
	def get_file(self, path):
		self.api.get('{}/names/{}'.format(self.root_hash, name))
		# stores in cwdir, so load the files into memory and delete them
		secret = self.file_to_memory('{}/{}/secret'.format(os.getcwd(), name))
		os.rmdir('{}/{}'.format(os.getcwd(), name))

	# interface funcs
	def exists(self, query):
		if query == None:
			return False
		return True

	def check_name(self, name):
		# will look at local fs because syncing is asyncronous to code
		return os.path.isdir('{}/{}/names/{}'.format(os.getcwd(), self.root_dir, name))

	def add_name(self, name, n, e):

		# create new packages directory
		self.new_dir('{}/{}/packages/{}'.format(os.getcwd(), self.root_dir, name))
		
		# create new names directory
		self.new_dir('{}/{}/names/{}'.format(os.getcwd(), self.root_dir, name))

		# add public key files to names
		self.new_file('{}/{}/names/{}/n'.format(os.getcwd(), self.root_dir, name), n)
		self.new_file('{}/{}/names/{}/e'.format(os.getcwd(), self.root_dir, name), e)

		self.update_fs()
		
		return self.check_name(name)

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
			self.new_file('{}/names/{}/secret'.format(os.getcwd(), name), secret)
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

		self.new_dir('{}/packages/{}/{}'.format(os.getcwd(), owner, package))
		self.new_file('{}/packages/{}/{}/template'.format(os.getcwd(), owner, package), template)
		self.new_file('{}/packages/{}/{}/example'.format(os.getcwd(), owner, package), example)

		return self.check_package(owner, package)

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
			'template' : query[0],
			'example' : query[1]
		}

	def check_package(self, owner, package):
		query = self.connection.execute("SELECT * FROM packages WHERE owner='{}' AND package='{}'".format(owner, package)).fetchone()
		return self.exists(query)

	def get_key(self, name):
		return self.connection.execute("SELECT n, e FROM names WHERE name='{}'".format(name)).fetchone()

	def set_secret(self, name, secret):
		self.connection.execute("UPDATE names SET secret=? WHERE name=?", (secret, name))
		return self.exists(self.get_secret(name))

	def get_secret(self, name):
		return self.connection.execute("SELECT secret FROM names WHERE name='{}'".format(name)).fetchone()[0]

	def add_package(self, owner, package, template, example):
		self.connection.execute('INSERT INTO packages VALUES (?,?,?,?)', (owner, package, template, example))
		return self.check_package(owner, package)