from api import IPFS_Engine

ipfs = IPFS_Engine('127.0.0.1', 5001, None, 'ipfs')
print(ipfs.check_name('poopoo'))
ipfs.add_name('poopoo', '123', '456')