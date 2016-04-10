var bodyParser = require('body-parser');
var boot = require('loopback-boot');
var loopback = require('loopback');
var path = require('path');
var app = module.exports = loopback();
var engine = require('ejs-locals');
var helmet = require('helmet');



app.middleware('initial', bodyParser.urlencoded({ extended: true }));

// Bootstrap the application, configure models, datasources and middleware.
// Sub-apps like REST API are mounted via boot scripts.
boot(app, __dirname);

app.set('view engine', 'ejs'); // LoopBack comes with EJS out-of-box

// must be set to serve views properly when starting the app via `slc run` from
// the project rootapp.set('views', path.join(__dirname, 'views'));

app.set('views', path.join(__dirname, 'views'));
app.engine('ejs', engine);
app.use(loopback.static(require('path').join(__dirname, '..', 'client')));
app.use(loopback.static(require('path').join(__dirname, '..', 'bower_components')));

app.use(helmet.xssFilter());

// Implement X-Frame: Deny
app.use(helmet.xframe());

// Hide X-Powered-By
app.use(helmet.hidePoweredBy());

app.middleware('session:before', loopback.cookieParser(app.get('cookieSecret')));
app.middleware('session', loopback.session({
  secret: 'kitty',
  saveUninitialized: true,
  resave: true
}));



app.start = function() {
  // start the web server
  return app.listen(function() {
    app.emit('started');
    console.log('Web server listening at: %s', app.get('url'));
  });
};

// start the server if `$ node server.js`
if (require.main === module) {
  app.start();
}

