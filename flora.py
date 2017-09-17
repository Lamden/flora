import sqlite3
import click
import subprocess
import time
import pickle
import requests
import rsa
import os

API_LOCATION = 'http://127.0.0.1:5000'
KEY_LOCATION = os.path.expanduser('~/.flora')

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

		if os.path.exists(KEY_LOCATION) == False:
			os.mkdir(KEY_LOCATION)

		# save to disk
		with open('{}/.key'.format(KEY_LOCATION), 'wb') as f:
		    pickle.dump((pub, priv), f, pickle.HIGHEST_PROTOCOL)

		r = requests.post('{}/names'.format(API_LOCATION), data = {'name' : name, 'n' : pub.n, 'e' : pub.e})
		if r.json() == True:
			print('successfully registered')
		else:
			print('error registering name')

@cli.command()
@click.argument('name')
def check(name):
	# hit api to see if name is already registered
	if check_name(name) == True:
		print('already registered')
	else:
		print('available to register')

@cli.command()
@click.argument('name')
def authorize(name):
	# hit api to see if name is already registered
	r = requests.get('{}/auth'.format(API_LOCATION), data = {'name' : name})
	
	# request will return secret. decrypt and send info back to server
	(pub, priv) = pickle.load(open('{}/.key'.format(KEY_LOCATION), 'rb'))
	message = rsa.decrypt(eval(r.json()), priv)
	print(message)

@cli.command()
@click.argument('package')
def install():
	print(package)

@cli.command()
def upload():
	pass