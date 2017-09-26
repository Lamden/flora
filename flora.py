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
import api

API_LOCATION = 'http://127.0.0.1:5000'
KEY_LOCATION = os.path.expanduser('~/.flora')
api.main()
def check_package_name_format(name):
	split_string = name.split('/')
	if len(split_string) != 2:
		return False
	return split_string

def check_name(name):
	return requests.get('{}/names'.format(API_LOCATION), data = {'name':name}).json()

@click.group()
def cli():
	pass

# registers a new username
@cli.command()
@click.argument('name')
def register(name):
	import pdb;pdb.set_trace()
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
@click.argument('name')
def check(name):
	# hit api to see if name is already registered
	print(check_name(name)['message'])

@cli.command()
@click.argument('package_name')
def install(package_name):
	split_string = check_package_name_format(package_name)
	if split_string == False:
		print('Invalid format. Propose a package name such that <owner>/<package_name>.')
		return
	owner = split_string[0]
	package = split_string[1]
	r = requests.get('{}/packages'.format(API_LOCATION), data = {'owner' : owner, 'package' : package})
	print(r.json()['data']['template'])
	print(r.json()['data']['example'])
	# ask where to save files
	project_folder = ''
	project_folder = input('Directory to save package (enter for current working directory):')
	project_folder = os.getcwd() if project_folder == '' else project_folder

	package_dir = os.path.join(project_folder, package_name)
	os.makedirs(package_dir)

	with open(os.path.join(package_dir, 'template.tsol'), 'w') as f:
		f.write(r.json()['data']['template'])

	with open(os.path.join(package_dir, 'example.tsol'), 'w') as f:
		f.write(str(r.json()['data']['example']))

	print('Package successfully pulled!')

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

	assert tsol.does_compile(code, example), 'Errors in code.'

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
	print(r.json()['message'])
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