const vorpal = require('vorpal')();
const sync = require('sync');
const IPFS = require('ipfs-daemon/src/ipfs-node-daemon')
const OrbitDB = require('orbit-db')
const fs = require('fs')
const path = require('path')
const Promise = require('promise')
const solc = require('solc')
const handlebars = require('handlebars')

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

function readFile(filename){
  return new Promise(function (fulfill, reject){
    fs.readFile(filename, function (err, data) {
      if (err) {
        throw reject(err)
      }
      fulfill(data.toString())
    });
  });
}

function get(db, arg) {
  return new Promise(function (fulfill, reject){
    fulfill(db.get(arg))
  });
}

function compile(code) {
  return new Promise(function (fulfill, reject){
    var output = solc.compile(code, 1)
    if (output.errors.length > 0) {
      reject(output.errors)
    }
    else {
      fulfill(output)
    }
  });
}

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
  .option('-n, --name <n>')
  .option('-e, --example <e>')
  .description('Uploads a new .tsol package to the IPFS package database.')
  .action(function (args, callback) {

    // load file
    readFile(path.join(__dirname, args.fileName))
      .then((data) => {
        return data
      })
      .then((file) => {
        readFile(path.join(__dirname, args.options.example))
        .then((data => {
          return [file, data]
        }))
        .then((data) => {
          var contract = data[0]
          var example = data[1]

          // prepare document to upload
          var doc = {
            _id : args.options.name,
            sol : contract,
            example : JSON.parse(example),
            filename : args.fileName
          }
          console.log(doc)
          // make sure the package does not already exist on ipfs
          get(db, args.options.name)
            .then((results) => {
              if (results.length > 0) {
                throw 'Package with provided name already exists online. Choose another.'
              }
              else {

                // if not, lets make sure its valid solc
                var template = handlebars.compile(doc.sol)
                var sol = template(doc.example)

                var output = solc.compile(sol, 1)
                if (Object.keys(output.contracts).length > 0) {
                  // it builds, upload it to the database
                  db.put(doc)
                  .then((hash) => {
                    console.log(hash)
                    callback();
                  });
                } 
              }
              
            });
        })
      })
  });

// vorpal
//   .delimiter('flora$')
//   .show();

vorpal.parse(process.argv)