import sqlite3
import ipfsapi
import click
import subprocess
import time
import pickle

# where's the pickle?
MASTER_DB_HASH = 0

# timeout for daemon launch
TIMEOUT = 2

def connect():
	print('Connecting to IPFS...')
	return ipfsapi.connect('127.0.0.1', 5001)

api = None
proc = None
try:
	api = connect()
except Exception as e:
	# start daemon
	print('IPFS Daemon not running, starting now...')
	proc = subprocess.Popen(['ipfs', 'daemon'], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
	time.sleep(TIMEOUT)
	try:
		api = connect()
	except:
		raise 'Timeout error.'

print('Connected to IPFS.')

@click.command()
def cli():
	"""This script showcases different terminal UI helpers in Click."""
	pass

# @cli.command()
# def install():
# 	click.echo('package')

if proc != None:
	print('Killing IPFS Daemon...')
	proc = subprocess.Popen(['killall', 'ipfs'], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
	print('Done.')