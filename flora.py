import click
from ipfs import IPFS

# where's the pickle?
MASTER_DB_HASH = 0

@click.group()
def cli():
	"""This script showcases different terminal UI helpers in Click."""
	print(IPFS)
	print('howdy')

@cli.command()
def install():
	click.echo('package')
	#if proc != None:
	#IPFS.kill()