# Flora
### An Enterprise Grade Distributed Smart Contract Package Manager

#### Get Started
```
pip install flora
```

OR for the latest version

```
git clone https://github.com/Lamden/flora.git
python setup.py develop
flora --help
```

#### Commands
```
flora install <username/package>
flora check <desired username>
flora register <desired username>
flora upload <your username/package name>

coming soon:
flora list <username>
flora pull or flora stage instead of flora install
flora generate <username/package> (more info on this later)
```

Flora is a distributed smart contract package manager for [Ethereum](https://github.com/ethereum) and other smart contract blockchains. It uses [Apache Cassandra](https://github.com/apache/cassandra) as a performant and enterprise grade datastore which allows the contents of the system to be distributed across participants of the Lamden system. This unique sharding method makes sure that there is always a replicated piece of data available and is self-healing when nodes go down. It's used currently by massive Fortune 500 companies as a way to guarantee uptime.

Flora solves to industry problem of community members gravitating towards certain authorities such as [OpenZeppelin](https://github.com/OpenZeppelin/zeppelin-solidity/tree/master/contracts) for smart contracts without a workflow tool that guarantees who you are pulling the file from. Flora uses encrypted secrets and PGP keys to maintain identity and information is never passed between server and client unencrypted.

Flora will also soon support inline imports using our [Templated Solidity](https://github.com/Lamden/tsol) paradigm so that you no longer have to copy and paste from GitHub repositories when you want to include the same piece of code over and over again. This will accelerate the concept of inheritance which leads to more complex data types and more interesting pieces of technology being developed.

#### "But I thought you were going to use [IPFS?](https://github.com/ipfs/ipfs)"

Upon multiple implementation attempts, we were not able to produce a system that does not sacrifice the core tenents of what we want Flora to be. This diverges from the initial white paper.

The reason being that while IPFS is cool software, it is still in the alpha phase and has not been load tested by enterprises. We want to develop a system that is easy to use, follows current standards, and has been industry tested. [Apache Cassandra](https://github.com/apache/cassandra) was developed at Facebook initially, went through the Apache program, and is now an official open-source Apache system that is being used today in mission critical applications.

#### Uploading Packages
A better guide will come soon, but when uploading packages, you need to point to a directory that contains a .tsol file and a .json payload that compiles. Compilation checks occur on client and server sides, so you will know if there is a problem with the files you are uploading.

Not in the mood to learn our [Templated Solidity](https://github.com/Lamden/tsol)? No problem. Just point to a Solidity file that has the extension .tsol, and create an empty .json file. We will support regular .sol files soon.
