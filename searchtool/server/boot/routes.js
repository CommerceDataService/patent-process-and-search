module.exports = function(app) {
    var router   = app.loopback.Router();
    var unirest  = require('unirest');
    var config   = require('../server-config.js');
    var fs       = require('fs');
    var path     = require('path');
    var search   = require('./search');
    var User     = app.models.user;


    router.get('/', function(req, res) {
        res.redirect('/login');
    });

    // Default Login Screen
    router.get('/login', function(req, res){
        res.render('login');
    });


    // Login Post and set session cookie
    router.post('/login', function(req, res) {
        User.login({
            email: req.body.email,
            password: req.body.password
        }, 'user', function(err, token) {
            if (err) {
                console.log(err);
                res.render('login-response', { //render view named 'login-response.ejs'
                    title: 'Login failed',
                    content: 'Please Contact Thomas Beach for access if you do not have a login',
                    redirectTo: '/login',
                    redirectToLinkText: 'Try again'
                });
                return;
            } else {
                token = token.toJSON();
                var maxAgeSet=10000000;  // Darren : 166 Mins .. I know long.
                res.cookie('USPTOSession', JSON.stringify(token), {
                    maxAge: maxAgeSet,
                    httpOnly: true
                });

                res.render('newview', {
                    email: req.body.email,
                    accessToken: token.id,
                    accessOK: !!(token.id || ! config.requireLogin)
                });
            }
        });
    });

    // Destroy session on logout
    router.get('/logout', function(req, res, next) {
        if (!req.cookies.USPTOSession) return res.sendStatus(401);
        var sessionCookie = JSON.parse(req.cookies.USPTOSession);
        console.log(sessionCookie.id);
        var AccessToken = app.models.AccessToken;
        var token = new AccessToken({
            id: sessionCookie.id
        });
        token.destroy();
        req.session.destroy();
        res.clearCookie('USPTOSession');

        res.redirect('/login');
    });



    router.get('/help', function(req, res) {
        res.render('help');
    });

    // Main Search
    router.get('/newsearch', function(req, res, next) {
        var sessionCookie;
        if (config.requireLogin) {
            if (typeof req.cookies.USPTOSession === 'undefined') {
                res.redirect('/login');
            } else {
                sessionCookie = JSON.parse(req.cookies.USPTOSession);
                if (typeof sessionCookie.id === 'undefined') {
                    res.redirect('/login');
                }
            }
        }
        next();
    }, function(req, res) {
        search.buildSearch(req, res);
    });

    // Download Query
    router.get('/download', function(req, res) {
        //console.log(req);
        //var q = req.body.q;

        var q;
        if (req.query.q) {
            q=req.query.q.toString();
        }

        var s = 0;
        var currentPage = 1;
        if (req.query.pageno && req.query.pageno > 0) {
            s = (req.query.pageno -1) *20;
            currentPage = parseInt(req.query.pageno) ;
        }
        var SEARCH_URL= config.solrURI+'/oafiledatanew/select?q='+q+'&wt=csv&indent=false&rows=2000&start='+s+'&q.op=AND&fl=appid,action_type,filename,minread,id,textdata';

        // Create the filename for the CSV and remove any special characters
        var csvfilename = q;
        csvfilename=csvfilename.replace(/\"/g,'');
        csvfilename=csvfilename.replace(/\'/g,'');
        csvfilename=csvfilename.replace(/\)/g,'');
        csvfilename=csvfilename.replace(/\(/g,'');
        csvfilename=csvfilename.replace(/\]/g,'');
        csvfilename=csvfilename.replace(/\[/g,'');
        csvfilename=csvfilename.replace(/\:/g,'');
        csvfilename=csvfilename.replace(/\n/g,'');
        csvfilename=csvfilename.replace(/\r/g,'');
        csvfilename=csvfilename.replace(/\//g,'');
        csvfilename=csvfilename.replace(/\\/g,'');
        csvfilename=csvfilename.replace(/\“/g,'');
        csvfilename=csvfilename.replace(/\”/g,'');
        csvfilename=csvfilename.replace(/<[^\w<>]*(?:[^<>"'\s]*:)?[^\w<>]*(?:\W*s\W*c\W*r\W*i\W*p\W*t|\W*f\W*o\W*r\W*m|\W*s\W*t\W*y\W*l\W*e|\W*s\W*v\W*g|\W*m\W*a\W*r\W*q\W*u\W*e\W*e|(?:\W*l\W*i\W*n\W*k|\W*o\W*b\W*j\W*e\W*c\W*t|\W*e\W*m\W*b\W*e\W*d|\W*a\W*p\W*p\W*l\W*e\W*t|\W*p\W*a\W*r\W*a\W*m|\W*i?\W*f\W*r\W*a\W*m\W*e|\W*b\W*a\W*s\W*e|\W*b\W*o\W*d\W*y|\W*m\W*e\W*t\W*a|\W*i\W*m\W*a?\W*g\W*e?|\W*v\W*i\W*d\W*e\W*o|\W*a\W*u\W*d\W*i\W*o|\W*b\W*i\W*n\W*d\W*i\W*n\W*g\W*s|\W*s\W*e\W*t|\W*i\W*s\W*i\W*n\W*d\W*e\W*x|\W*a\W*n\W*i\W*m\W*a\W*t\W*e)[^>\w])|(?:<\w[\s\S]*[\s\0\/]|['"])(?:formaction|style|background|src|lowsrc|ping|on(?:d(?:e(?:vice(?:(?:orienta|mo)tion|proximity|found|light)|livery(?:success|error)|activate)|r(?:ag(?:e(?:n(?:ter|d)|xit)|(?:gestur|leav)e|start|drop|over)?|op)|i(?:s(?:c(?:hargingtimechange|onnect(?:ing|ed))|abled)|aling)|ata(?:setc(?:omplete|hanged)|(?:availabl|chang)e|error)|urationchange|ownloading|blclick)|Moz(?:M(?:agnifyGesture(?:Update|Start)?|ouse(?:PixelScroll|Hittest))|S(?:wipeGesture(?:Update|Start|End)?|crolledAreaChanged)|(?:(?:Press)?TapGestur|BeforeResiz)e|EdgeUI(?:C(?:omplet|ancel)|Start)ed|RotateGesture(?:Update|Start)?|A(?:udioAvailable|fterPaint))|c(?:o(?:m(?:p(?:osition(?:update|start|end)|lete)|mand(?:update)?)|n(?:t(?:rolselect|extmenu)|nect(?:ing|ed))|py)|a(?:(?:llschang|ch)ed|nplay(?:through)?|rdstatechange)|h(?:(?:arging(?:time)?ch)?ange|ecking)|(?:fstate|ell)change|u(?:echange|t)|l(?:ick|ose))|m(?:o(?:z(?:pointerlock(?:change|error)|(?:orientation|time)change|fullscreen(?:change|error)|network(?:down|up)load)|use(?:(?:lea|mo)ve|o(?:ver|ut)|enter|wheel|down|up)|ve(?:start|end)?)|essage|ark)|s(?:t(?:a(?:t(?:uschanged|echange)|lled|rt)|k(?:sessione|comma)nd|op)|e(?:ek(?:complete|ing|ed)|(?:lec(?:tstar)?)?t|n(?:ding|t))|u(?:ccess|spend|bmit)|peech(?:start|end)|ound(?:start|end)|croll|how)|b(?:e(?:for(?:e(?:(?:scriptexecu|activa)te|u(?:nload|pdate)|p(?:aste|rint)|c(?:opy|ut)|editfocus)|deactivate)|gin(?:Event)?)|oun(?:dary|ce)|l(?:ocked|ur)|roadcast|usy)|a(?:n(?:imation(?:iteration|start|end)|tennastatechange)|fter(?:(?:scriptexecu|upda)te|print)|udio(?:process|start|end)|d(?:apteradded|dtrack)|ctivate|lerting|bort)|DOM(?:Node(?:Inserted(?:IntoDocument)?|Removed(?:FromDocument)?)|(?:CharacterData|Subtree)Modified|A(?:ttrModified|ctivate)|Focus(?:Out|In)|MouseScroll)|r(?:e(?:s(?:u(?:m(?:ing|e)|lt)|ize|et)|adystatechange|pea(?:tEven)?t|movetrack|trieving|ceived)|ow(?:s(?:inserted|delete)|e(?:nter|xit))|atechange)|p(?:op(?:up(?:hid(?:den|ing)|show(?:ing|n))|state)|a(?:ge(?:hide|show)|(?:st|us)e|int)|ro(?:pertychange|gress)|lay(?:ing)?)|t(?:ouch(?:(?:lea|mo)ve|en(?:ter|d)|cancel|start)|ime(?:update|out)|ransitionend|ext)|u(?:s(?:erproximity|sdreceived)|p(?:gradeneeded|dateready)|n(?:derflow|load))|f(?:o(?:rm(?:change|input)|cus(?:out|in)?)|i(?:lterchange|nish)|ailed)|l(?:o(?:ad(?:e(?:d(?:meta)?data|nd)|start)?|secapture)|evelchange|y)|g(?:amepad(?:(?:dis)?connected|button(?:down|up)|axismove)|et)|e(?:n(?:d(?:Event|ed)?|abled|ter)|rror(?:update)?|mptied|xit)|i(?:cc(?:cardlockerror|infochange)|n(?:coming|valid|put))|o(?:(?:(?:ff|n)lin|bsolet)e|verflow(?:changed)?|pen)|SVG(?:(?:Unl|L)oad|Resize|Scroll|Abort|Error|Zoom)|h(?:e(?:adphoneschange|l[dp])|ashchange|olding)|v(?:o(?:lum|ic)e|ersion)change|w(?:a(?:it|rn)ing|heel)|key(?:press|down|up)|(?:AppComman|Loa)d|no(?:update|match)|Request|zoom))[\s\0]*=/g,'');
        csvfilename=csvfilename.replace(/ /g,'-');
        csvfilename = csvfilename + '.csv';
        // End Create File ame

        if (typeof req.query.q !== 'undefined') {
            unirest.get(SEARCH_URL)
                .end(function (response) {
                    var csv;
                    if (typeof response.body !== 'undefined') {
                        csv = response.body;
                    }
                    //console.log(response);
                    if (typeof response.body !== 'undefined') {
                        res.setHeader('Content-disposition', 'attachment; filename='+csvfilename);
                        res.set('Content-Type', 'text/csv');
                        res.status(200).send(csv);
                        //res.redirect('/');
                    } else {
                        res.setHeader('Content-disposition', 'attachment; filename='+csvfilename);
                        res.set('Content-Type', 'text/csv');
                        res.status(200).send(csv);
                        //res.redirect('/');
                    }

                });
        } else {
            res.render('newview', {
                email: req.body.email,
                accessOK: !!(! config.requireLogin || token.id)
            }
            );
        }
    });

    app.use(router);

};
