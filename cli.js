const vorpal = require('vorpal')();
const sync = require('sync');
const IPFS = require('ipfs-daemon/src/ipfs-node-daemon')
const OrbitDB = require('orbit-db')
var fs = require('fs')
var solc = require('solc')

const floraID = '2ed4ab81-b91e-4d88-a64f-02d82c623b97'

const ipfs = new IPFS()
const orbitdb = new OrbitDB(ipfs)
const db = orbitdb.docstore(floraID)

/*

document template

{
  _id:'package name'
  sol:'source code'
  filename:'how to save it'
}

*/

vorpal
  .command('install <packageName>')
  .description('Attempts to install a Solidity smart contract from the IPFS package database.')
  .action(function (args, callback) {
    results = db.get(args.packageName)
    console.log(results)
    callback();
  });

vorpal
  .command('upload <fileName>')
  .option('-n, --name')
  .option('-e', '--example')
  .description('Uploads a new .tsol package to the IPFS package database.')
  .action(function (args, callback) {

    // load file
    payload = null
    fs.readFile( args.fileName, function (err, data) {
      if (err) {
        throw err; 
      }
      payload = data.toString()
    });

    // prepare document to upload
    doc = {
      _id : args.options.name,
      sol : payload,
      example : args.options.example,
      filename : args.fileName
    }

    // check if it already exists on the package manager
    results = db.get(args.options.name)

    if (results.length > 0) {
      throw 'Package with provided name already exists online. Choose another.';
    }

    //db.get(args.packageName)
    callback();
  });

// vorpal
//   .delimiter('flora$')
//   .show();

vorpal.parse(process.argv)