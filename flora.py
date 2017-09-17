import sqlite3
import click
import subprocess
import time
import pickle
import requests

API_LOCATION = 'http://127.0.0.1:5000'

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
		print('lets do it')

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