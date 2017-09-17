from flask import Flask, request
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
import os
import re

DB_NAME = 'sqlite:///test.db'

e = create_engine(DB_NAME)

app = Flask(__name__)
api = Api(app)

def check_name(conn, name):
	query = conn.execute("SELECT * FROM names WHERE name='{}'".format(name)).fetchone()
	if query != None:
		return True
	return False

def clean(s):
	return re.sub('[^A-Za-z0-9]+', '', s)

class NameRegistry(Resource):
	def get(self):
		name = request.form['name']
		conn = e.connect()
		#Perform query and return JSON data
		return check_name(conn, name)

	def post(self):
		name = request.form['name']
		key = request.form['key']
		conn = e.connect()
		query = conn.execute('INSERT INTO names VALUES (?,?)', (name, key))
		return check_name(conn, name)

# GET does not require auth and just downloads packages
# POST required last secret. Secret is then flushed so auth is required again before POSTing again
class PackageRegistry(Resource):
	def get(self):
		#TODO
		pass

	def post(self):
		#TODO
		pass

# GET gets a new secret signed by public key for user
# secret signed and stored in server with server key (PGP?)
# server key supplied in memory at each start up
class Authorization(Resource):
	def get(self):
		#TODO
		pass

app = Flask(__name__)
api = Api(app)

api.add_resource(NameRegistry, '/names')
api.add_resource(PackageRegistry, '/packages')
api.add_resource(Authorization, '/auth')

if __name__ == '__main__':
    app.run(debug=True)