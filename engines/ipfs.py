import ipfsapi
from ipfsapi.encoding import Encoding
from engine import Engine
import logging
import os
import requests

class IPFS_Engine(Engine):
	def __init__(self, ip, port, root_url='https://flora.lamden.io/apiv1', root_dir='/', root_hash=None):
		'''
		Parameters: ip, port, root_hash, root_dir = ('127.0.0.1',
													5000,
													'Qx87yhjudysudf65fg424242blahblah',
													'~/.lamden/flora/')
				   (ip: str, port: int, root_hash: hash, root_dir: str)
		'''
		try:
			self.log = logging.getLogger(resource_filename(__name__, __file__))
			self.api = ipfsapi.connect(ip, port)
			self.root_hash = root_hash
			self.enc = Encoding()
		except:
			raise Exception('Daemon not running')
		self.root_dir = os.environ.get('FLORA_ROOT')
		self.root_pkgs = os.path.join(self.root_dir, 'packages')
		self.root_names = os.path.join(self.root_dir, 'names')
		self.root_url = root_url
		self.virt_tree = self.api.ls(requests.get(os.path.join(root_url, '/root_hash')).read()).get('Objects')

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
		except Exception as e:
			raise e

	def file_to_memory(self, path):
		data = None
		with open(path, 'r') as d:
			data = d.read()
		os.remove(path)
		return data

	def get_file(self, path):
		# *args, **kwargs passed to requests
		stream, headers = self.api.get(f'{self.root_names}/{name}',
										recursive=False)
		return self.enc.parse(stream), headers

	# interface funcs
	def exists(self, query):
		if query == None:
			return False
		return True

	def check_name(self, name):
		# will look at local fs because syncing is asyncronous to code
		return os.path.isdir(f'{self.root_names}/{name}')

	def add_name(self, name, n, e):
		# *args, **kwargs passed to requests
		stream, headers = self.api.add(f'{self.root_path}/{n}', recursive=True)
		return self.enc.parse(stream), headers

	def get_package(self, owner, package):
		# *args, **kwargs passed to requests
		self.api.get(self.root_pkgs)

	def check_package(self, owner, package):
		current_tree = self.api.ls(self.root_hash)
		return path_exists(current_tree, owner, package)

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

	def get_named_secret(self, name):
		try:
			# pull named_secret from ipfs
			self.api.get(f'{self.root_hash}/names/{name}')
			# stores in cwdir, so load the files into memory and delete them
			secret = self.file_to_memory(f'{os.getcwd()}/{name}/secret')
			os.rmdir('{}/{}'.format(os.getcwd(), name))

			return secret
		except:
			return False

	def add_package(self, owner, package, tar_gz_stream):
		def update_link(owner, package, link_hash):
			respone = requests.post(self.root_url, data=json.dumps({"owner": owner,
														  "package": package,
														  "link_hash": link_hash}))
			self.root_hash = response.data
			return new_root_hash

		link_hash = self.api.add_bytes(tar_gz_stream)
		update_link(owner, package, link_hash)

	def sync(self):
		try:
			request = self.api.add(self.root_path, recursive=True)
			# request[-1]['Hash']
			self.log.info(request.data)
		except:
			raise Exception(f'Unable to sync {self.root_path}')
