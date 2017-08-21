const vorpal = require('vorpal')();

vorpal
  .command('install <packageName>')
  .action(function (args, callback) {
    let str = args.packageName;
    this.log(str);
    callback();
  });

vorpal
  .command('upload <fileName>')
  .action(function (args, callback) {
    let str = args.fileName;
    this.log(str);
    callback();
  });

vorpal
  .delimiter('flora$')
  .show();