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
hbs.registerHelper('convertDocCode', function(code){
  var documentCodeDictionary ={
    'M327-D': 'PUB OTHER MISCELLANEOUS COMMUNICATION TO APPLICANT',
    'CTNF': 'NON-FINAL REJECTION',
    'CNTA': 'ALLOWABILITY NOTICE',
    'CTFR': 'FINAL REJECTION',
    'CNOA': 'CORRECTED NOTICE OF ALLOWABILITY',
    'N271': 'RESPONSE TO AMENDMENT UNDER RULE 312',
    'REXD': 'RX - EX PARTE REEXAM ORDER - DENIED',
    'EX.R': 'REASONS FOR ALLOWANCE',
    'RTDE': 'RX - PETITION DECISION - DENIED',
    'INTNO': 'INTERFERENCE NOTIFICATION TO PATENTEE RULE 607',
    'L.SI': 'SUSPENSION - INTERFERENCE IN ANOTHER CASE',
    'RXBPAI': 'REEXAM FORWARDED TO BOARD OF PATENT APPEALS AND INTERFERENCES',
    'RXSRXI': 'DECISION STAYING REEXAM PROCEEDING IN FAVOR OF INTERFERENCE PROCEEDING',
    'CTMS': 'MISCELLANEOUS ACTION WITH SSP',
    'M327': 'MISCELLANEOUS COMMUNICATION TO APPLICANT - NO ACTION COUNT',
    'M327-E': 'BOA MISCELLANEOUS COMMUNICATION TO APPLICANT',
    'P132': 'MISCELLANEOUS COMMUNICATION',
    'R327': 'RX - MISCELLANEOUS COMMUNICATION TO APPLICANT',
    'RXM327': 'MISCELLANEOUS COMMUNICATION TO APPLICANT',
    'RXMISC': 'MISCELLANEOUS ACTION MAILED',
    'RXMMIS': 'MISCELLANEOUS LETTER MAILED',
    'SEMI': 'SE - MISCELLANEOUS DECISION/OFFICE NOTICE IN SE',
    'RTGR': 'RX - PETITION DECISION - GRANTED',
    'RTDI': 'RX - PETITION DECISION - DISMISSED'
  };
  return new hbs.SafeString(documentCodeDictionary[code]);
});

hbs.registerHelper('hyperlinkIt', function(source, appid){
  switch(source){
    case 'palm': return new hbs.SafeString('http://palmapps.uspto.gov/cgi-bin/expo/GenInfo/snquery.pl?APPL_ID='+appid);
    case 'dav': return new hbs.SafeString('http://dav.uspto.gov/webapp/applicationViewer.html?casenumber='+appid)
  }
})
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
