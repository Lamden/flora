from api import IPFS_Engine

ipfs = IPFS_Engine('127.0.0.1', 5001, None, 'ipfs')
# ipfs.add_name('stuart', '123', '123')
print(ipfs.check_name('poopoo'))
print(ipfs.check_name('stuart'))
# print(ipfs.check_package('poopoo', 'erc20'))
print(ipfs.get_key('stuart'))