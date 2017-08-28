import sqlite3
import ipfsapi
import click
import subprocess
import time

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
	time.sleep(2)
	api = connect()

print('Connected to IPFS.')

@click.group()
def cli():
    """This script showcases different terminal UI helpers in Click."""
    pass

@cli.command()
def install():
	click.echo('package')

cli.add_command(install)