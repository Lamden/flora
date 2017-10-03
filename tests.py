import pytest
from engines.sql import SQL_Engine
from engines.ipfs import IPFS_Engine
from flask import Flask, request
import string
import random
import time
def random_string(length):
    pool = string.ascii_letters + string.digits
    return ''.join(random.choice(pool) for i in range(length))

DB_NAME = 'sqlite:///test.db'

def abstract_test_engine_add_name(engine):

	name = random_string(10)
	n = random_string(10)
	e = random_string(10)
	
	assert engine.add_name(name, n, e) == True, 'Name not added. Expected True. Got False'

def abstract_test_engine_add_package(engine):
	
	owner = random_string(10)
	package = random_string(10)
	template = random_string(10)
	example = random_string(10)

	success = engine.add_package(owner, package, template, example)
	
	payload = engine.get_package(owner, package)
	assert success and payload['template'] == template and payload['example'] == example, 'Package not added.'

def abstract_test_engine_get_key(engine):

	name = random_string(10)
	n = random_string(10)
	e = random_string(10)

	engine.add_name(name, n, e)
	assert engine.get_key(name) == (n, e), 'Key not returned'


def test_sql():
	sql = SQL_Engine(DB_NAME)
	abstract_test_engine_add_name(sql)
	abstract_test_engine_add_package(sql)
	abstract_test_engine_get_key(sql)

def test_ipfs():
	ipfs = IPFS_Engine('127.0.0.1', 5001, None, 'ipfs')
	abstract_test_engine_add_name(ipfs)
	abstract_test_engine_add_package(ipfs)
	abstract_test_engine_get_key(ipfs)