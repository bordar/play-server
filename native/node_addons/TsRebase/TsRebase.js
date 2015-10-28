var tsRebase = require('./build/Release/TsRebase.node');
var fs = require('fs');

if (process.argv.length < 3) {
	console.log('Usage:\n\tnode TsRebase.js <file1> <file2> <file3> ...');
	process.exit(1);
}

var rebaseContext = {};

for (var i = 2; i < process.argv.length; i++) {
	var curFileName = process.argv[i];
	var curBuffer = fs.readFileSync(curFileName);
	rebaseContext = tsRebase.rebaseTs(rebaseContext, curBuffer);
	fs.writeFileSync(curFileName, curBuffer);
}
