const vorpal = require('vorpal')();
const fsAutocomplete = require('vorpal-autocomplete-fs');
const sync = require('sync');
const IPFS = require('ipfs-daemon/src/ipfs-node-daemon')
const OrbitDB = require('orbit-db')
const fs = require('fs')
const path = require('path')
const solc = require('solc')
const handlebars = require('handlebars')

const floraID = '2ed4ab81-b91e-4d88-a64f-02d82c623b97'

const ipfs = new IPFS()
const orbitdb = new OrbitDB(ipfs)
const db = orbitdb.docstore(floraID)


vorpal
  .delimiter('flora:')
  .show();

/*

document template

{
  _id:'package name'
  sol:'source code'
  filename:'how to save it'
}

*/

function get(key) {
  console.log('get key: ', key)
  var value = db.get(key)
  console.log('value: ', value)
  if (value.length > 0) return Promise.reject('Package with provided name already exists online. Choose another.')
  return Promise.resolve(value)
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

function readFile(fn){
  return new Promise((resolve, reject)=>{
    fs.readFile(fn, (err, data)=>{
      if (err){
        reject(err)
      }
      else{
        resolve(data)
      }
    })  
  })
  
}

vorpal
  .command('install <packageName>')
  .description('Attempts to install a Solidity smart tsol from the IPFS package database.')
  .action(function (args, callback) {
    var results = db.get(args.packageName);
    console.log(results)
    callback();
  });

vorpal
  .command('ls [dir]')
  .option('-d, --dir [d]')
  .description('list files in current dir')
  .action(function (args, callback) {
    if (args.options.example)
    {
      fs.readdir(args.options.example, (err, files) => {
        files.forEach(file => {
          console.log(file);
        });
      })
    }
    else
    {
      fs.readdir('.', (err, files) => {
        files.forEach(file => {
          console.log(file);
        });
      })
    }
  })


vorpal
  .command('upload <fileName>')
  .autocomplete(fsAutocomplete())
  .option('-n, --name <n>')
  .option('-e, --example <e>')
  .description('Uploads a new .tsol package to the IPFS package database.')
  .action(function (args, callback) {
    // load files    
    var package = [readFile(path.join(__dirname, args.fileName)),
                   readFile(path.join(__dirname, args.options.example)),
                   get(args.options.name)]

    Promise.all(package)
      .then(values =>{
        var [tsol_buf, json_buf, db_value] = values;
// TODO : create a package.json type file so we don't have to type 140+
// chars to do an upload
        var doc = {
          _id : args.options.name,
          sol : tsol_buf.toString(),
          example : JSON.parse(json_buf.toString()),
          filename : args.fileName
        }
        // if not, lets make sure its valid solc
        var template = handlebars.compile(doc.sol)
        var sol = template(doc.example)
        var output = solc.compile(sol, 1)
        console.log('DONE')
      })
      .catch(e => {
        console.warn('Unable to upload', e.toString())
      })
  })

vorpal.parse(process.argv)