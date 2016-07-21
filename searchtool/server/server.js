var loopback = require('loopback');
var boot = require('loopback-boot');
var app = module.exports = loopback();

// Passport configurators..
var loopbackPassport = require('loopback-component-passport');
var PassportConfigurator = loopbackPassport.PassportConfigurator;
var passportConfigurator = new PassportConfigurator(app);

/*
 * body-parser is a piece of express middleware that
 *   reads a form's input and stores it as a javascript
 *   object accessible through `req.body`
 *
 */
var bodyParser = require('body-parser');

/**
 * Flash messages for passport
 *
 * Setting the failureFlash option to true instructs Passport to flash an
 * error message using the message given by the strategy's verify callback,
 * if any. This is often the best approach, because the verify callback
 * can make the most accurate determination of why authentication failed.
 */
var flash      = require('express-flash');

// attempt to build the providers/passport config
var config = {};
try {
  config = require('../providers.json');
} catch (err) {
  console.trace(err);
  process.exit(1); // fatal
}

// -- Add your pre-processing middleware here --


var path = require('path');
var helmet = require('helmet');
var hbs = require('hbs');
var helpers = require('./helpers.js');


app.middleware('initial', bodyParser.urlencoded({ extended: true }));

// Bootstrap the application, configure models, datasources and middleware.
// Sub-apps like REST API are mounted via boot scripts.
boot(app, __dirname);

app.set('view engine', 'hbs'); // LoopBack comes with EJS out-of-box
// must be set to serve views properly when starting the app via `slc run` from
// the project rootapp.set('views', path.join(__dirname, 'views'));

app.set('views', path.join(__dirname, 'views'));
app.use('/client', loopback.static(path.join(__dirname, '../client')));
app.use('/bower_components', loopback.static(path.join(__dirname, '../bower_components')));

app.use(helmet.xssFilter());

// Implement X-Frame: Deny
app.use(helmet.xframe());

// Hide X-Powered-By
app.use(helmet.hidePoweredBy());

app.middleware('session:before', loopback.cookieParser(app.get('cookieSecret')));
app.middleware('session', loopback.session({
  secret: 'kitty',
  saveUninitialized: true,
  resave: true,
}));
passportConfigurator.init();

// We need flash messages to see passport errors
app.use(flash());

passportConfigurator.setupModels({
  userModel: app.models.user,
  userIdentityModel: app.models.userIdentity,
  userCredentialModel: app.models.userCredential,
});
for (var s in config) {
  var c = config[s];
  c.session = c.session !== false;
  passportConfigurator.configureProvider(s, c);
}
var ensureLoggedIn = require('connect-ensure-login').ensureLoggedIn;

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
