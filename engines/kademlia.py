from engine import Engine
from twisted.application import service, internet
from twisted.python.log import ILogObserver
from twisted.internet import reactor, task

import sys, os
sys.path.append(os.path.dirname(__file__))
from kademlia.network import Server
from kademlia import log

class Kademlia_Engine(Engine):
	def __init__(self, *args):
		self.ip = args[0]
		self.port = args[1]

		application = service.Application("kademlia")
		application.setComponent(ILogObserver, log.FileLogObserver(sys.stdout, log.INFO).emit)

		if os.path.isfile('cache.pickle'):
		    kserver = Server.loadState('cache.pickle')
		else:
		    kserver = Server()
		    kserver.bootstrap([(self.ip, self.port)])
		kserver.saveStateRegularly('cache.pickle', 10)

		server = internet.UDPServer(self.port, kserver.protocol)
		server.setServiceParent(application)
		
		self.log = logging.getLogger(resource_filename(__name__, __file__))

	def done(result):
    	return result

    def returnValue(key):
    	return server.get(f'{key}').addCallback(done)

	def exists(self, query):
		if query == None:
			return False
		return True

	def check_name(self, name):
		return self.exists(server.get(f'{name}.key').addCallback(done))

	def add_name(self, name, n, e, verification):
		key = f'{name}.key'
		return self.exists(server.set(key, (n, e)).addCallback(returnValue(key)))

	def get_package(self, owner, package):
		return server.get(f'{owner}/{package}').addCallback(done)

	def check_package(self, owner, package):
		return self.exists(server.get(f'{owner}/{package}').addCallback(done))

	def get_key(self, name):
		return server.get(f'{name}.key').addCallback(done)

	def add_package(self, owner, package, template, example, verification):
		raise NotImplementedError()

	