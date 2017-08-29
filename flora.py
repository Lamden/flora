import sqlite3
import ipfsapi
import click
import subprocess
import time
import pickle

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

def start_up():
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

def tear_down():
	# if a subprocess was started by this script, assume the user doesn't want it 
	# running after it's done, and vice versa, so kill it if needed
	if IPFS.proc != None:
		print('Killing IPFS Daemon...')
		proc = subprocess.Popen(['killall', 'ipfs'], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
		print('Done.')

@click.group()
@click.option('-t', '--timeout', default=3, help='Timeout in seconds per connection attempt to IPFS.')
@click.option('-r', '--retries', default=10, help='Number of IPFS connection attempts before giving up.')
def cli(timeout, retries):
	TIMEOUT = timeout
	RETRIES = retries
	start_up()

@cli.command()
@click.option('-f', '--filepath', default=3, help='Path to install template. Will assume current working directory.')
@click.option('-n', '--name', default=3, help='Name of package to install.')
def install():
	tear_down()

@cli.command()
@click.option('-f', '--filepath', default=3, help='Path to Template Solidity Contract to upload.')
@click.option('-e', '--example', default=3, help='Path to Example Payload to upload.')
@click.option('-n', '--name', default=3, help='Name to call package.')
def upload():
	tear_down()