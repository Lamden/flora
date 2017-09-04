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

@cli.command()
def push():
    click.echo('push')
    # TODO
    # xz --robot --info-memory
    # XZ_DEFAULTS
    # XZ_OPT
    # XZ_OPT=${XZ_OPT-"-7e"}
    # xz -cvfJ -7 git.repo.tar.xz this_git_repo
    # ipfs add
    # ipns route
    # return hash and address info


def create_an_account():
    #     place public key in db
    raise Exception('TODO')

def create_repo():
    #     verify public key in db
    #     hash = deploy xz compressed git repo to ipfs with developer pub key in metadata
    #     insert repo_hash in db
    raise Exception('TODO')

def push_repo():
    #     verify public key in db
    #     get prev_repo_hash
    #     new_repo_hash = deploy xz compressed git repo to ipfs with developer pub key in metadata
    #     chain prev_repo_hash, new_repo_hash
    #     insert new_repo_hash
    #         where
    #         pub_key=?
    #         AND prev_repo_hash=?
    raise Exception('TODO')