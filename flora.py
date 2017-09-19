import sqlite3
import click
import subprocess
import time
import pickle
import requests
import rsa
import os
from simplecrypt import encrypt, decrypt

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
		print('{} already registered.'.format(name))
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
			print('Successfully registered new name: {}'.format(name))
		else:
			print('Error registering name: {}'.format(name))

@cli.command()
@click.argument('name')
def check(name):
	# hit api to see if name is already registered
	if check_name(name) == True:
		print('{} already registered.'.format(name))
	else:
		print('{} is available to register.'.format(name))

@cli.command()
@click.argument('name')
def authorize(name):
	# hit api for secret
	r = requests.get('{}/auth'.format(API_LOCATION), data = {'name' : name})
	
	# request will return secret. decrypt and send info back to server
	(pub, priv) = pickle.load(open('{}/.key'.format(KEY_LOCATION), 'rb'))
	message = rsa.decrypt(eval(r.json()), priv)
	print(r.json())
	print(message)

@cli.command()
@click.argument('package')
def install():
	print(package)

@cli.command()
@click.argument('package_name')
def upload(package_name):
	split_string = package_name.split('/')
	if len(split_string) != 2:
		print('Invalid format. Propose a package name such that <owner>/<package_name>.')
		return

	owner = split_string[0]
	package = split_string[1]
	
	# to replace authorize because you don't need it
	r = requests.get('{}/packages'.format(API_LOCATION), data = {'owner' : owner, 'package' : package})

	# check to see if there was a success (the package is available)
	if r.json()['status'] == 'success':

		# if so, decrypt the secret
		secret = r.json()['data']
		(pub, priv) = pickle.load(open('{}/.key'.format(KEY_LOCATION), 'rb'))
		cipher = rsa.decrypt(eval(secret), priv)

		# continue uploading
		user_input = input('Test data: ')

		# sign data
		message = encrypt(cipher, user_input.encode('utf8'))

		# post data
		data = message
		r = requests.post('{}/packages'.format(API_LOCATION), data = {'owner' : owner, 'package' : package, 'data' : str(data)})

		print(eval(r.json()))
	else:
		print('no')