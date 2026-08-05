// Usage: localhost:3333/ml?parameter=arguments
// The child_process.spawn returns an object with stdout and stderr streams. 
// The spawn is best used to when you want the child process to return 
// a large amount of data to Node - image processing, reading binary data etc.
// $ npm install express-handlebars
// sudo apt-get install libpq-dev
// $ sudo npm -g install node-gyp
// $ npm install zmq
// $ DEBUG=* node iot_script.js
// $ su
// # npm install zerorpc
// $ nohup node iot_app.js &
// $ npm install pg

const express = require('express');
const app = express();
const express_handlebars = require('express-handlebars');
const path = require('path');
//var zerorpc = require("zerorpc");
//var zmq = require('zeromq');
//var zmq = require('/usr/lib/nodejs/node_modules/zeromq');
//var zmq_socket = zmq.socket('sub');
//zmq_socket.bindSync('tcp://127.0.0.1:5000');

var options = {
  args: ['value1', 'value2', 'value3']
};

app.engine('.hbs', express_handlebars({
  defaultLayout: 'main',
  extname: '.hbs',
  layoutsDir: path.join(__dirname, 'views/layouts')
}))

app.set('view engine', '.hbs')

app.set('views', path.join(__dirname, 'views'))

app.use('/static', express.static(__dirname + '/static'));

var server = app.listen(3001, () => console.log('Usage on browser: http://localhost:3001/predict'));

var io = require('socket.io').listen(server);

//var db_client = require("pg");

//var uri = "postgres://demo:demo@192.168.3.2:5432/demo?sslmode=require";

// npm install pg --save
const { Client } = require('pg')

const db_client = new Client({
  host: '192.168.3.2',
  port: 5432,
  user: 'demo',
  password: 'demo',
  database: 'demo',
  //timezone: 'UTC'
})

db_client.connect((err) => {

  if (err) {

    console.error('Connection error', err.stack)

  } else {

    console.log('Database is connected.')
  }
})

var previous_output_timestamp = null;

var output_timestamp = null;
//var output_place = null;
//var output_meter = null;
var output_feature = null;

var output_feature_previous = null;

var output_value = null;

var input_timestamp = null;
//var input_place = null;
//var input_meter = null;
var input_feature = null;

var input_feature_previous = null;

var input_value = null;

var equals_timestamp = null;

var timestamp_different = false;

var INTERVAL_TIME = 1000



setInterval(function() {

  // LOOP: PUBLISH INPUT AND OUTPUT

  // CHECK WHETHER RECEIVED MESSAGE HAS DIFFERENT TIMESTAMP THAN PREVIOUS TIMESTAMP

  //INPUT DATASET

  console.log('\nLOOP: ' + previous_output_timestamp);

  //TODO: WHERE timestamp, place, meter, feature EQUALS
  if(previous_output_timestamp != null) {

    //db_client.query('SELECT timestamp AT TIME ZONE ' + "'UTC'" + ', place, meter, feature, value FROM input_dataset WHERE timestamp=$1;', [previous_output_timestamp], (error, result) => {

    /* db_client.query('SELECT timestamp AT TIME ZONE ' + "'UTC'" + ', feature, value FROM input_dataset WHERE timestamp=$1;', [previous_output_timestamp], (error, result) => {

    var row = null;

    try {

      console.log('\nINPUT QUERY\n');

      row = JSON.stringify(result.rows);

      if (row != null && result.rows != null) {

        console.log(row);

        row_parse = JSON.parse(row);

        if (row_parse != null && row_parse[0] != null) {

          console.log(row_parse);

          // UTC TIMEZONE
          input_timestamp = row_parse[0].timezone;
          //LOCAL TIME
          //input_timestamp = row_parse[0].timestamp;
          //input_place = row_parse[0].place;
          //input_meter = row_parse[0].meter;
          input_feature = row_parse[0].feature;
          input_value = row_parse[0].value;

          console.log(input_timestamp)
          //console.log(input_place)
          //console.log(input_meter)
          console.log(input_feature)
          console.log(input_value)

        }

      }

    } catch (error) {

      console.log('error: ', error)

    } 

   }) */

  }

    var table = 'water_output'

    var column_name = 'feature'

    var column_value = 'ai_ss1_ss';

  //OUTPUT DATASET
  //db_client.query('SELECT timestamp AT TIME ZONE ' + "'UTC'" + ', place, meter, feature, value FROM output_dataset ORDER BY timestamp DESC LIMIT 1;', (error, result) => {
    //db_client.query('SELECT feature, timestamp AT TIME ZONE ' + "'UTC'" + ', value FROM ' + table + ' ORDER BY timestamp DESC LIMIT 1;', (error, result) => {

    // SELECT feature, timestamp, value FROM water_output WHERE feature LIKE 'ai_ss1_ss';
    db_client.query('SELECT feature, timestamp, value FROM ' + table + ' WHERE ' + column_name + ' LIKE ' + "'" + column_value + "'" + ' ORDER BY timestamp DESC LIMIT 1;', (error, result) => {

    //console.log('\nDATABASE QUERY:\n' + result + ' \n ' + error);

    //console.log(result)

    //var objs = [];
    //for (var i = 0;i < result.length; i++) {
    //  objs.push({timestamp: result[i].rows});
    //}
    //console.log(objs)

    var row = null;

    previous_output_timestamp = null;

    console.log('\nDATABASE QUERY:');

    try {

      if (result != null && result.rows != null) {

        row = JSON.stringify(result.rows);

        console.log('row',row);

        row_parse = JSON.parse(row);

        console.log('row_parse',row_parse);

        if (row_parse != null && row_parse[0] != null) {

          // UTC TIMEZONE
          //output_timestamp = row_parse[0].timezone;
          // LOCAL TIME
          output_timestamp = row_parse[0].timestamp;
          //output_timestamp = row_parse[0].timestamp;
          //output_place = row_parse[0].place;
          //output_meter = row_parse[0].meter;
          output_feature = row_parse[0].feature;
          output_value = row_parse[0].value;

          console.log('output_timestamp',output_timestamp)
          //console.log('output_place',output_place)
          //console.log('output_meter',output_meter)
          console.log('output_feature',output_feature)
          console.log('output_value',output_value)

          //previous_output_timestamp = output_timestamp;

          previous_output_timestamp = output_timestamp.split(".")[0];

          previous_output_timestamp = previous_output_timestamp.replace('T'," ");

          console.log('\nprevious_output_timestamp', previous_output_timestamp);

          console.log('\nequals_timestamp', equals_timestamp);

          if (previous_output_timestamp != equals_timestamp) {

            equals_timestamp = output_timestamp.split(".")[0];

            equals_timestamp = equals_timestamp.replace('T'," ");

            timestamp_different = true;

            if (output_feature_previous == null) {

            	output_feature_previous = output_feature;

            }

          } else {

             console.log('\n\nprevious_output_timestamp equals to ', equals_timestamp);

             timestamp_different = false

          }

          //var previous_output_dateformat = new Date(output_timestamp);

          //previous_output_timestamp = previous_output_dateformat.toLocaleDateString() + ' ' + previous_output_dateformat.toTimeString().substring(0, d.toTimeString().indexOf("GMT"));

        }
      }

    } catch (error) {

      console.log('error: ', error)

    }

    //db_client.end()

  })

  //if (output_place == input_place && output_meter == input_meter && output_feature == input_feature) {

    //if (output_feature == input_feature) {

    if(previous_output_timestamp != null && timestamp_different == true && output_feature == output_feature_previous) {

      // PLACE = "HVSB"
      // METER = "HVSB_S_B2_G001-J03"
      // FEATURE = "voltage_B"

      //var data = { timestamp : previous_output_timestamp, place : output_place, meter : output_meter, feature : output_feature, predicted : output_value, history : input_value, log : ""};
      //var data = { timestamp : previous_output_timestamp, feature : output_feature, predicted : output_value, history : input_value, log : ""};

      var data = { timestamp : previous_output_timestamp, feature : output_feature, predicted : output_value, log : ""};

      publish_dataset(data);

      console.log('\ndata', data);

    }
  //}

},INTERVAL_TIME);

//var db_query = db_client.query('SELECT timestamp, place, meter, feature, value FROM output_dataset ORDER BY timestamp DESC LIMIT 1;');

/*db_query.on("row", function (row, result) {
    result.addRow(row);
});

db_query.on("end", function (result) {
    console.log(JSON.stringify(result.rows, null, "    "));
    client.end();
});*/

//INPUT DATASE

//Parameterized query with a callback:



//var python_script_client = new zerorpc.Client();

//python_script_client.connect("tcp://127.0.0.1:4242");

//python_script_client.invoke("subscribe", function(error, res, more) {

//	console.log("invoke: " + res);

//});

//function FloatGenerator(minValue, maxValue, precision) {

//    return ((Math.random() * (maxValue * precision - minValue * precision) + minValue * precision).toFixed(precision));
//};

//io.sockets.on('connection', function (socket) {
//io.on('connection', function (socket) {

	//console.log("A client is connected to socket.");

	//TODO: FETCH ML DATA FROM PYTHON MESSAGE QUEUE

	//setInterval(function() {

		//var temp_local_date = new Date();

		//var hours = temp_local_date.getHours();
        //hours = ("0" + hours).slice(-2);

        //var minutes = temp_local_date.getMinutes();
        //minutes = ("0" + minutes).slice(-2);

        //var seconds = temp_local_date.getSeconds();
        //seconds = ("0" + seconds).slice(-2);

        //var temp_time =  hours + ':' + minutes + ':' + seconds;

		//var data = {
		//	x : temp_time,
		//	y : FloatGenerator(800,815,1)
		//};

		//io.emit('update', data);

	//}, 5000);

//});

//status = zmq_socket.subscribe("get_status");

//zmq_socket.subscribe('message');

//console.log(status);

//zmq_socket.on('message', function(data) {

 //   console.log(data.toString());

    //io.emit('chart', data); 
//});

//const { exec } = require('child_process');

//var spawn = require('child_process').spawn;

//var process = spawn('python3', ['./iot_script.py',"server"], {

//    stdio:[null, null, null, 'ipc']

//});

/*

 > SELECT timestamp, place, meter, feature, value FROM output_dataset ORDER BY timestamp DESC LIMIT 1;

*/

function publish_dataset(data) {

  console.log('publish_dataset');

  io.emit('update', data);

  console.log('data:', data);

}

/*process.on('message', function(data) {

	

  	console.log('iot_app received from iot_script: ' + " " + data.data.timestamp + " " + data.data.predicted + " " + data.data.history, + " " + data.log);

  	var data = { timestamp : data.data.timestamp, predicted : data.data.predicted, history : data.data.history, log : data.log};

  	io.emit('update', data);

});

process.on('exit', (code) => {

    console.log("exit" + code);
});

process.stdout.on('data', (data) => {
  console.log(data.toString());
});

process.stderr.on('data', (data) => {
  console.log(data.toString());
});

process.on('close', () => {
  console.log('close');
});


process.on('disconnect', () => {
  console.log('disconnect');
})*/


app.get('/predict', (req, res) => {

    var text = "unknown";

    if(req.query.parameter != null && req.query.parameter.length > 0) {

    	text = req.query.parameter;
    }

    //var process = spawn('python3', ['./ml_script.py',req.query.parameter]);

	//var process = exec('python3 ml_script.py ' + text, function (err, stdout, stderr) {

	//	console.log(stdout);

	//});


	//status = zmq_socket.subscribe("get_status");

	//console.log("EXECUTE PYTHON SCRIPT");


	//process.stdout.on('data', function(data) {

		//res.send(data.toString());

		//res.send("OK");

		//res.render('./page.html', {data: data});

        //res.send(data.toString());

        //console.log(data.toString());

        //res.send(data);

        //console.log(data.toString());

        //io.emit('chart', data); 

    //}) 

	//res = 'success';

	//TODO: EXECUTE PYTHON SCIRPT

	//return res;
	//zmq_socket.bindSync('tcp://127.0.0.1:5000');

	//zmq_socket.subscribe('message');

	//zmq_socket.on('message', function(data) {

    	//console.log(data.toString());

    //io.emit('chart', data); 
	//});

	//res.send("OK");

	res.render('home', {
      //Handlebars variables on .hbs file
    	//place : '',
      //meter : '',
      //feature : ''
  	})
})