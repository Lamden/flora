from io import StringIO
import sys
import sqlite3
import click
import subprocess
import time
import pickle
import requests
import rsa
import os
import glob
import json
import tsol
from simplecrypt import encrypt, decrypt
import string
import random

lamden_home = os.environ.get('LAMDEN_HOME', None)
lamden_folder_path = os.environ.get('LAMDEN_FOLDER_PATH', None)
lamden_db_file = os.environ.get('LAMDEN_DB_FILE', None)

API_LOCATION = 'http://127.0.0.1:5000'
KEY_LOCATION = os.path.expanduser('~/.flora')

def random_string(length):
    pool = string.ascii_letters + string.digits
    return ''.join(random.choice(pool) for i in range(length))

def check_package_name_format(name):
	split_string = name.split('/')
	if len(split_string) != 2:
		return False
	return split_string

def check_name(name):
	return requests.get('{}/names'.format(API_LOCATION), data = {'name':name}).json()

def split_package_name(name):
	# takes input as <username> / <package> , <implementation> and returns a payload for it

	# splitting of arguments into lists
	user_and_package = name.split('/')
	package_and_implemenation = None
	
	if ',' in str(user_and_package[1]):
		package_and_implemenation = str(user_and_package[1]).split(',')

	payload = {
		'username' : None,
		'package' : None,
		'implementation' : None
	}

	# explicit construction of the payload. not pretty, but functional
	payload['username'] = user_and_package[0]

	if package_and_implemenation != None:
		payload['package'] = package_and_implemenation[0]
		payload['implementation'] = package_and_implemenation[1]
	else:
		try:
			payload['package'] = user_and_package[1]
		except:
			pass

	# error catching for arguments that end with '/' or ',' and split into a list of 2 with an empty 2nd index
	payload['package'] = None if payload['package'] == '' else payload['package']
	payload['implementation'] = None if payload['implementation'] == '' else payload['implementation']

	return payload

@click.group()
def cli():
	print('===     THIS SOFTWARE IS NOT PRODUCTION READY       ===')
	print('===     THIS VERSION IS FOR TEST PURPOSES ONLY      ===')
	print('=== PACKAGES UPLOADED MAY BE DELETED IN MIGRATIONS. ===')
	pass

@cli.command()
@click.argument('name')
def check(name):
	# hit api to see if name is already registered
	print(check_name(name)['message'])

#TODO
def staging():
	stdin_text = click.get_text_stream('stdin')
	for line in stdin_text:
		print(line)

# registers a new username
@cli.command()
@click.argument('name')
def register(name):
	# hit api to see if name is already registered
	if check_name(name)['status'] == 'error':
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
		if r.json()['status'] == 'success':
			print('Successfully registered new name: {}'.format(name))
		else:
			print('Error registering name: {}'.format(name))

@cli.command()
@click.argument('package_name')
@click.argument('location')
def pull(package_name, location):
	# no args should parse from a requirements.txt file recursively

	if location == 'here':
		print('yes')

	if location == 'home':
		print('ye')

@cli.command()
@click.argument('package_name')
@click.option('--location', prompt='Where to save (here = ./, home = current project home)')
def install(package_name, location):
	split_string = check_package_name_format(package_name)
	if split_string == False:
		print('Invalid format. Propose a package name such that <owner>/<package_name>.')
		return
	owner = split_string[0]
	package = split_string[1]
	r = requests.get('{}/packages'.format(API_LOCATION), data = {'owner' : owner, 'package' : package})

	# ask where to save file
	try:
		d = r.json()['data']

		print(d['template'])
		print(d['example'])

		r.json()['data']['template']

		project_folder = ''
		if location != 'here' or location != 'home':
			# ask where to save files
			project_folder = location

		if location == 'here':
			project_folder = os.getcwd()

		if location == 'home':
			project_folder = lamden_home

		package_dir = os.path.join(project_folder, package_name)
		os.makedirs(package_dir)

		with open(os.path.join(package_dir, 'template.tsol'), 'w') as f:
			f.write(r.json()['data']['template'])

		with open(os.path.join(package_dir, 'example.tsol'), 'w') as f:
			f.write(str(r.json()['data']['example']))

		print('Package successfully pulled!')

	except:
		print(r.json()['message'])

@cli.command()
@click.argument('package_name')
def stage():
	# check the chain folder for contracts
	sol_files = os.path.join(settings.lamden_folder_path, 'contracts/*.sol')
	pass

@cli.command()
@click.argument('package_name')
def upload(package_name):
	# check if package name valid
	split_string = check_package_name_format(package_name)
	if split_string == False:
		print('Invalid format. Propose a package name such that <owner>/<package_name>.')
		return

	# ask where the project directory
	project_folder = ''
	project_folder = input('Path of project folder (enter for current working directory):')
	project_folder = os.getcwd() if project_folder == '' else project_folder

	# try to find the files
	code_path = glob.glob(os.path.join(project_folder, '*.tsol'))
	example = glob.glob(os.path.join(project_folder, '*.json'))

	assert len(code_path) > 0 and len(example) > 0, 'Could not find *.tsol and *.json files in provided directory.'

	# pop off the first file name and turn the code into a file object
	code = open(code_path[0])

	# turn the example into a dict
	with open(example[0]) as e:
		example = json.load(e)

	tsol.compile(code, example)
	#assert tsol.does_compile(code, example), 'Errors in code.'

	print('*.tsol and *.json compiled with 0 errors. Proceeding to upload.')

	payload = {
		'tsol' : open(code_path[0]).read(),
		'example' : example
	}

	owner = split_string[0]
	package = split_string[1]

	# to replace authorize because you don't need it
	r = requests.get('{}/package_registry'.format(API_LOCATION), data = {'owner' : owner, 'package' : package})

	# check to see if there was a success (the package is available)
	print(r.text)
	if r.json()['status'] == 'success':

		# if so, decrypt the secret
		secret = r.json()['data']
		(pub, priv) = pickle.load(open('{}/.key'.format(KEY_LOCATION), 'rb'))
		cipher = rsa.decrypt(eval(secret), priv)

		print('Encrypting package...')

		# sign data
		payload = json.dumps(payload)
		message = encrypt(cipher, payload)

		# post data
		data = message
		print('Uploading to Flora under {}/{}...'.format(owner, package))
		r = requests.post('{}/package_registry'.format(API_LOCATION), data = {'owner' : owner, 'package' : package, 'data' : str(data)})

		print(r.json()['message'])
	else:
		print(r.json()['message'])

@cli.command()
@click.argument('package_name')
def list(package_name):
	# lists all of the packages for a user, or all of the implementations for a package

	# <username> / <package> , <implementation>

	# detemine if there's a user and package, or just a user
	p = split_package_name(package_name)
	if p['username'] != None:
		# get all of the packages and print their names in a pretty print
		if p['package'] != None:
			# get all implementations and print their names in a pretty print
			if p['implementation'] != None:
				print('Cannot list one specific implementation. Use "print".')
				return
			return
		return

	print('Error parsing arguments. Got {}. Specify in format such that: <username>/<package> with <package> being optional.'.format(p))

# @cli.command()
# @click.argument('payload')
# def print(payload):

# 	pass
