import sqlite3
import ipfsapi
import subprocess
import time
import pickle

TIMEOUT = 2
RETRIES = 3

class IPFS(object):
	def __init__(self):
		self.api = None
		self.proc = None
		try:
			self.api = connect()
		except Exception as e:
			# if not, start daemon
			print('IPFS Daemon not running, starting now...')
			self.proc = subprocess.Popen(['ipfs', 'daemon'], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
			retry = 0
			while retry > RETRIES:
				# wait a second to let it start
				time.sleep(TIMEOUT)
				try:
					self.api = connect()
					break
				except:
					print('Timed out...')
					retry += 1
				# repeat connect attempts until retries are satisfied
			if retry == RETRIES:
				# throw error if it went through all the retries
				raise Error('Could not connect...')

		# otherwise continue
		print('Connected to IPFS.')

	def connect(self):
		print('Connecting to IPFS...')
		return ipfsapi.connect('127.0.0.1', 5001)

	def kill(self):
		if self.proc != None:
			print('Killing IPFS Daemon...')
			subprocess.Popen(['killall', 'ipfs'], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
			print('Done.')

IPFS = IPFS()