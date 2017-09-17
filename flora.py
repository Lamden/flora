import sqlite3
import click
import subprocess
import time
import pickle
import requests

@click.group()
def cli():
	pass

@click.command()
@click.argument('name')
def register(name)
	print(name)

@cli.command()
def install():
	pass

@cli.command()
def upload():
	pass