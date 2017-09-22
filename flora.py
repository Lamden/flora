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

from simplecrypt import encrypt, decrypt

# tsol libs
from solc import compile_source, compile_standard
from jinja2 import Environment
from jinja2.nodes import Name
from io import BytesIO

API_LOCATION = 'http://127.0.0.1:5000'
KEY_LOCATION = os.path.expanduser('~/.flora')

def check_name(name):
	return requests.get('{}/names'.format(API_LOCATION), data = {'name':name}).json()

# copied directly from saffron contracts.py and slightly modified
# should be abstracted into its own tsol library eventually
def get_template_variables(fo):
	nodes = Environment().parse(fo.read()).body[0].nodes
	var_names = [x.name for x in nodes if type(x) is Name]
	return var_names

def render_contract(payload):
	sol_contract = payload.pop('sol')
	template_variables = get_template_variables(BytesIO(sol_contract.encode()))
	assert 'contract_name' in payload
	name = payload.get('contract_name')
	assert all(x in template_variables for x in list(payload.keys()))
	template = Environment().from_string(sol_contract)
	return name, template.render(payload)

def load_tsol_file(file=None, payload=None):
	assert file and payload, 'No file or payload provided.'
	payload['sol'] = file.read()
	name, rendered_contract = render_contract(payload=payload)
	return name, rendered_contract

input_json = '''{"language": "Solidity", "sources": {
				"{{name}}": {
					"content": {{sol}}
				}
			},
			"settings": {
				"outputSelection": {
					"*": {
						"*": [ "metadata", "evm.bytecode", "abi", "evm.bytecode.opcodes", "evm.gasEstimates", "evm.methodIdentifiers" ]
					}
				}
			}
		}'''

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
	
	# ask where the project directory
	project_folder = ''
	project_folder = input('Path of project folder (enter for current working directory):')
	project_folder = os.getcwd() if project_folder == '' else project_folder

	# try to find the files
	code = glob.glob(os.path.join(project_folder, '*.tsol'))
	example = glob.glob(os.path.join(project_folder, '*.json'))

	assert len(code) > 0 and len(example) > 0, 'Could not find *.tsol and *.json files in provided directory.'

	# pop off the first file name and turn the code into a file object
	code = open(code[0])

	# turn the example into a dict
	with open(example[0]) as e:    
		example = json.load(e)

	# assert that the code compiles with the provided example
	solidity = load_tsol_file(code, example)
	compilation_payload = Environment().from_string(input_json).render(name=solidity[0], sol=json.dumps(solidity[1]))
	
	# this will throw an assertation error (thanks piper!) if the code doesn't compile
	compile_standard(json.loads(compilation_payload))

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
		message = (code.read(), example)
		user_input = input('Test data: ')

		# sign data
		message = encrypt(cipher, user_input.encode('utf8'))

		# post data
		data = message
		r = requests.post('{}/packages'.format(API_LOCATION), data = {'owner' : owner, 'package' : package, 'data' : str(data)})

		print(r.json())
	else:
		print('no')