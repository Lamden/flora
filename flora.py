import sqlite3
import ipfsapi
import click
import subprocess
import time
import pickle
#from ipfs import IPFS
# where's the pickle?
MASTER_DB_HASH = 0

# timeout for daemon launch
TIMEOUT = 3
RETRIES = 10

class IPFS(object):
	def __init__(self):
		self.api = None
		self.proc = None

IPFS = IPFS()

# connect to IPFS
def connect():
	print('Connecting to IPFS...')
	return ipfsapi.connect('127.0.0.1', 5001)

@click.group()
def cli():
	"""This script showcases different terminal UI helpers in Click."""
	# assume the daemon is running
	try:
		api = connect()
	except Exception as e:
		# if not, start daemon
		print('IPFS Daemon not running, starting now...')
		proc = subprocess.Popen(['ipfs', 'daemon'], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
		tries = 0
		while tries < RETRIES:
			time.sleep(TIMEOUT)
			try:
				api = connect()
			except:
				pass
			if api != None:
				break
			tries += 1

	# otherwise continue
	if api != None:
		print('Connected to IPFS.') 
	else:
		print('Could not connect to IPFS.')
	IPFS.api = api
	IPFS.proc = proc

@cli.command()
def install():
	if IPFS.proc != None:
		print('Killing IPFS Daemon...')
		proc = subprocess.Popen(['killall', 'ipfs'], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
		print('Done.')
	click.echo('package')

# if a subprocess was started by this script, assume the user doesn't want it 
# running after it's done, and vice versa, so kill it if needed
