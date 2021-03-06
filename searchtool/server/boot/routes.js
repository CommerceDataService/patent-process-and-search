// Copyright IBM Corp. 2015,2016. All Rights Reserved.
// Node module: loopback-example-access-control
// This file is licensed under the Artistic License 2.0.
// License text available at https://opensource.org/licenses/Artistic-2.0

module.exports = function(app) {
    var router   = app.loopback.Router();
    var unirest  = require('unirest');
    var config   = require('../server-config.js');
    var fs       = require('fs');
    var path     = require('path');
    var search   = require('./search');
    var User     = app.models.user;
    var ensureLoggedIn = require('connect-ensure-login').ensureLoggedIn;

    function protectedAccess() {
      if (config.requireLogin) {
        return ensureLoggedIn('/login');
      } else {
        return function(req, res, next) {
          req.user = {name: "Anonymous", id:0, email: 'anon@anonymous.org'};
          next();
        }
      }
    }

    router.get('/', function(req, res) {
      res.redirect('/help');
    });

    // Default Login Screen
    router.get('/login', function (req, res, next) {

      var errors;

      if (typeof(req.session.flash) !== 'undefined') {
          errors = req.session.flash['error'];
          console.log(errors);
      }

      res.render('login', {
        user: req.user,
        url: req.url,
        error: errors,
      });
    });

    router.get('/auth/logout', function(req, res, next) {
      req.logout();
      res.redirect('/');

    });



    router.get('/help', protectedAccess(), function(req, res) {
        res.render('help', {
            user: req.user,
        });
    });

    // Main Search
    router.get('/newsearch', protectedAccess(), function(req, res, next) {
        search.buildSearch(req, res);
    });


    // Download Query
    router.get('/download', function(req, res) {
      var q, fq, fields, rows;
      fq = "&fq=type:" + req.query.dataset;
      var dateRange='';
      // Only doing this for readiblity. Do not accept blank or undefined dates
      if ((typeof req.query.fromdate !== 'undefined' && req.query.todate !== 'undefined') &&  (req.query.fromdate.length > 2 && req.query.todate.length > 2)) {
          var fromDate = +new Date(req.query.fromdate)/1000;
          var toDate   = +new Date(req.query.todate)/1000;
          dateRange = 'doc_date:['+ fromDate+'%20TO%20'+toDate+']';
          fq += "&fq=" + dateRange;
      }

      // Ensure q var is cast to string
      if (req.query.q) {
          q=req.query.q.toString();
      }else{q="*:*";}

      // Art Unit Filter
      if ((typeof req.query.art_unit !== 'undefined') && (req.query.art_unit.length < 7) && (req.query.art_unit.length > 0)) {
        var artUnit = 'dn_dw_dn_gau_cd:' + req.query.art_unit;
        fq += "&fq=" + artUnit;
      }

          // Set documentcode filter
      if ((typeof req.query.documentcode !== 'undefined') && (req.query.documentcode.length > 0)) {
          documentcode = 'documentcode:' + req.query.documentcode;
          fq += "&fq=" + documentcode;
      }

      // Set Pagination to incremnt by 20 results
      var s = 0;
      var currentPage = 1;
      if (req.query.pageno && req.query.pageno > 0) {
          s = (req.query.pageno -1) *20;
          currentPage = parseInt(req.query.pageno) ;
      }

      //Set fields to return for query
      fields = 'type,appid,ifwnumber,documentcode,documentsourceidentifier,partyidentifier,groupartunitnumber,appl_id,\         file_dt,effective_filing_dt,inv_subj_matter_ty,appl_ty,dn_examiner_no,dn_dw_gau_cd,dn_pto_art_class_no,\
           dn_pto_art_subclass_no,confirm_no,dn_intppty_cust_no,atty_dkt_no,dn_nsrd_curr_loc_cd,dn_nsrd_curr_loc_dt,\
           app_status_no,app_status_dt,wipo_pub_no,patent_no,patent_issue_dt,abandon_dt,disposal_type,se_in,pct_no,\
           invn_ttl_tx,aia_in,continuity_type,frgn_priority_clm,usc_119_met,fig_qt,indp_claim_qt,efctv_claims_qt,\
           doc_date';
      rows = '100000';

      // Build Search .. if no page number set then only show
      var SEARCH_URL = config.solrURI+'/select?q={!q.op=AND df=textdata}'+q+fq+
        '&wt=csv&indent=false&rows='+rows+'&fl='+fields+'&start='+s;

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
                email: req.user,
            });
        }
    });

    app.use(router);

};
