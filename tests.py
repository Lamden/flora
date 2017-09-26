import pytest
from engines import SQL_Engine, IPFS_Engine
from flask import Flask, request
import string
import random

class Engine:
	def __init__(self, *args):
		raise NotImplementedError()
	def exists(self, query):
		raise NotImplementedError()
	def check_name(self, name):
		raise NotImplementedError()
	def add_name(self, name, n, e):
		raise NotImplementedError()
	def get_package(self, owner, package):
		raise NotImplementedError()
	def check_package(self, owner, package):
		raise NotImplementedError()
	def get_key(self, name):
		raise NotImplementedError()
	def set_secret(self, name, secret):
		raise NotImplementedError()
	def get_secret(self, name):
		raise NotImplementedError()
	def add_package(self, owner, package, template, example):
		raise NotImplementedError()

def random_string(length):
    pool = string.ascii_letters + string.digits
    return ''.join(random.choice(pool) for i in range(length))

DB_NAME = 'sqlite:///test.db'

def test_sql_add_name():
	sql = SQL_Engine(DB_NAME)
	name = random_string(10)
	n = random_string(10)
	e = random_string(10)
	assert sql.add_name(name, n, e), 'Name not added.'

def test_sql_add_package():
	sql = SQL_Engine(DB_NAME)
	
	owner = random_string(10)
	package = random_string(10)
	template = random_string(10)
	example = random_string(10)

	success = sql.add_package(owner, package, template, example)
	
	payload = sql.get_package(owner, package)
	assert success and payload['template'] == template and payload['example'] == example, 'Package not added.'

# def sql_test_get_key():
# 	pass

# def sql_test_set_secret():
# 	pass

# def sql_test_get_secret():
# 	pass