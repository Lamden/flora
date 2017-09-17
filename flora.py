import sqlite3
import click
import subprocess
import time
import pickle
import requests
import rsa

API_LOCATION = 'http://127.0.0.1:5000'
KEY_LOCATION = '~/.flora'

def check_name(name):
	return requests.get('{}/names'.format(API_LOCATION), data = {'name':name}).json()

@click.group()
def cli():
	pass

# registers a new username
@cli.command()
@click.argument('name')
def register(name):
	# hit api to see if name is already registered
	if check_name(name) == True:
		print('already registered')
	else:
		# generate new keypair
		(pub, priv) = rsa.newkeys(512)

		# save to disk
		with open(KEY_LOCATION, 'wb') as f:
		    pickle.dump((pub, priv), f, pickle.HIGHEST_PROTOCOL)

		r = requests.post('{}/names'.format(API_LOCATION), data = {'name' : name, 'key' : pub})
		print(r.json())

@cli.command()
@click.argument('name')
def check(name):
	# hit api to see if name is already registered
	if check_name(name) == True:
		print('already registered')
	else:
		print('available to register')

@cli.command()
@click.argument('package')
def install():
	print(package)

@cli.command()
def upload():
	pass