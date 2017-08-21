const vorpal = require('vorpal')();
const sync = require('sync');
const IPFS = require('ipfs-daemon/src/ipfs-node-daemon')
const OrbitDB = require('orbit-db')

const ipfs = new IPFS()

vorpal
  .command('install <packageName>')
  .description('Attempts to install a Solidity smart contract from the IPFS package database.')
  .action(function (args, callback) {
    let str = args.packageName;
    this.log(str);
    callback();
  });

vorpal
  .command('upload <fileName>')
  .description('Uploads a new package to the IPFS package database.')
  .action(function (args, callback) {
    let str = args.fileName;
    this.log(str);
    callback();
  });

// vorpal
//   .delimiter('flora$')
//   .show();

vorpal.parse(process.argv);