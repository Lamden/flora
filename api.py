from flask import Flask, request
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
import os
import re
import click
import rsa
import string
import random
from simplecrypt import encrypt, decrypt

DB_NAME = 'sqlite:///test.db'
KEY = None
engine = create_engine(DB_NAME)

def error_payload(message):
	return {
		"status": "error",
		"data": None,
		"message": message
	}

def success_payload(data, message):
	return {
		"status": "success",
		"data": data,
		"message": message
	}

def check_name(conn, name):
	query = conn.execute("SELECT * FROM names WHERE name='{}'".format(name)).fetchone()
	if query != None:
		return True
	return False

def check_package(conn, owner, package):
	query = conn.execute("SELECT * FROM packages WHERE owner='{}' AND package='{}'".format(owner, package)).fetchone()
	if query != None:
		return True
	return False

def clean(s):
	return re.sub('[^A-Za-z0-9]+', '', s)

def random_string(length):
    pool = string.ascii_letters + string.digits
    return ''.join(random.choice(pool) for i in range(length))

class NameRegistry(Resource):
	def get(self):
		name = request.form['name']
		conn = engine.connect()
		#Perform query and return JSON data
		return check_name(conn, name)

	def post(self):
		name = request.form['name']
		n = request.form['n']
		e = request.form['e']
		conn = engine.connect()
		query = conn.execute('INSERT INTO names VALUES (?,?,?,?)', (name, n, e, ''))
		return check_name(conn, name)

# GET does not require auth and just downloads packages. no data returns the DHT on IPFS or the whole SQL thing.
# POST required last secret. Secret is then flushed so auth is required again before POSTing again
class PackageRegistry(Resource):
	def get(self):
		# checks if the user can create a new package entry
		# if so, returns a new secret
		# user then must post the signed package to this endpoint
		owner = request.form['owner']
		package = request.form['package']

		conn = engine.connect()
		if not check_package(conn, owner, package):
			# try to pull the users public key
			conn = engine.connect()
			query = conn.execute("SELECT n, e FROM names WHERE name='{}'".format(owner)).fetchone()

			# in doing so, check if the user exists
			if query == None:
				return error_payload('Owner does not exist.')

			# construct the user's public key
			user_public_key = rsa.PublicKey(int(query[0]), int(query[1]))
			
			# create and store a new secret
			secret = random_string(53)
			query = conn.execute("UPDATE names SET secret='{}' WHERE name='{}'".format(secret, owner))
			
			# sign and send secret
			user_signed_secret = rsa.encrypt(secret.encode('utf8'), user_public_key)
			return success_payload(str(user_signed_secret), 'Package available to register.')
			
		else:
			return error_payload('Package already exists.')

	def post(self):
		owner = request.form['owner']
		package = request.form['package']
		data = request.form['data']
		print(data)
		# get the secret from the db
		conn = engine.connect()
		query = conn.execute("SELECT secret FROM names WHERE name='{}'".format(owner)).fetchone()
		print(query[0])

		plaintext = decrypt(query[0].encode('utf8'), eval(data))
		print(plaintext)
		return plaintext

# GET gets a new secret signed by public key for user
# secret signed and stored in server with server key (PGP?)
# server key supplied in memory at each start up
class Authorization(Resource):
	def get(self):
		name = request.form['name']
		# try to pull the users public key
		conn = engine.connect()
		query = conn.execute("SELECT n, e FROM names WHERE name='{}'".format(name)).fetchone()

		# in doing so, check if the user exists
		if query == None:
			return False

		# construct the user's public key
		user_public_key = rsa.PublicKey(int(query[0]), int(query[1]))
		
		# create and store a new secret
		secret = random_string(53)
		query = conn.execute("UPDATE names SET secret='{}' WHERE name='{}'".format(secret, name))
		
		# sign and send secret
		user_signed_secret = rsa.encrypt(secret.encode('utf8'), user_public_key)
		return str(user_signed_secret)

app = Flask(__name__)
api = Api(app)

api.add_resource(NameRegistry, '/names')
api.add_resource(PackageRegistry, '/packages')
api.add_resource(Authorization, '/auth')

if __name__ == '__main__':
	(pub, priv) = rsa.newkeys(512)
	KEY = (pub, priv)
	print(KEY)
	app.run(debug=True)
