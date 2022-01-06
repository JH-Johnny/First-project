var express = require('express');
var app = express();
var multer = require('multer');

var photo = multer({ storage:multer.diskStorage({
		destination: function (req, file, cb) {
			cb(null, 'photo/');
		},
		filename: function (req, file, cb) {
			cb(null, file.originalname);
		}
	})	
});

app.use('/photo', express.static('photo'));

app.listen(3000, function () {
  console.log('Example app listening on port 3000!');
});

app.post('/', photo.single('files'), function(req, res){
	console.log((req.body.timestamp) - (Date.now()/1000));
	console.log(req.body);
	console.log(req.file.path);
	res.send('');
});
