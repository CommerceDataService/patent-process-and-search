var bodyParser = require('body-parser');
var boot = require('loopback-boot');
var loopback = require('loopback');
var path = require('path');
var app = module.exports = loopback();
var helmet = require('helmet');
var hbs = require('hbs');



app.middleware('initial', bodyParser.urlencoded({ extended: true }));

// Bootstrap the application, configure models, datasources and middleware.
// Sub-apps like REST API are mounted via boot scripts.
boot(app, __dirname);

app.set('view engine', 'hbs'); // LoopBack comes with EJS out-of-box
hbs.registerHelper('truncate', function(passedString) {
    var theString = passedString.substring(0,900);
    return new hbs.SafeString(theString)
});
hbs.registerHelper('breaklines', function(text) {
    text = hbs.Utils.escapeExpression(text);
    text = text.replace(/(\r\n|\n|\r)/gm, '<br>');
    text = text.replace(/[&\/\\]/g,'_');
    return new hbs.SafeString(text);
});
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
