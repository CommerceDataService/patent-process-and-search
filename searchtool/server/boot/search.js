exports.buildSearch = function (req, res) {
    var config   = require('../server-config.js');
    var moment   = require('moment');
    var unirest  = require('unirest');
    var humanize = require('humanize');
    var paginate = require('nodejs-yapaginate/lib/main.js');


    // Get From Date
    var q, fq, validateMessage = {};
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
      q = q.replace('\'', '"').replace(/[\u201C\u201D]/g, '"');
      var qMarks = q.match(/"/g) || [];
      var openP = q.match(/\(/g) || [];
      var closeP = q.match(/\)/g) || [];
      if(qMarks && qMarks%2 !== 0){
          validateMessage.quotation = 'Check your query for missing quotation marks.';
        }
      if( openP.length !== closeP.length ){
          validateMessage.parenthesis = 'Check your query for missing parenthesis.';
      }

    }else{q="*:*";}

    // Art Unit Filter
    if (typeof req.query.art_unit !== 'undefined'){
      var artUnit = 'dn_dw_dn_gau_cd:' + req.query.art_unit;
      if(req.query.art_unit.length == 4) {
        fq += "&fq=" + artUnit;
      }else{
        validateMessage.artunit = 'Enter a valid 4-digit Art Unit number.'
      }
    }
        // Set documentcode filter
    if ((typeof req.query.documentcode !== 'undefined') && (req.query.documentcode.length > 0)) {
        if (typeof req.query.documentcode === 'object') {
            var reqArray = req.query.documentcode;
            var reqArrayLen = req.query.documentcode.length;
            var reqLoopVar = reqArrayLen - 1;
            var reqString = '';
            for (var i = reqLoopVar; i >0; i--) {
                reqString += reqArray[i] + "+OR+";
            }
            documentcode = 'documentcode:' +"("+ reqString + reqArray[0]+")";
            fq += "&fq=" + documentcode;
        } else {
            documentcode = 'documentcode:' + req.query.documentcode;
            fq += "&fq=" + documentcode;
        }
    }

    // Set Pagination to incremnt by 20 results
    var s = 0;
    var currentPage = 1;
    if (req.query.pageno && req.query.pageno > 0) {
        s = (req.query.pageno -1) *20;
        currentPage = parseInt(req.query.pageno) ;
    }

    // Build Search .. if no page number set then only show
    var SEARCH_URL = config.solrURI+'/select?q={!q.op=AND df=textdata}'+q+fq+'&wt=json&indent=true&rows=20&start='+s+'&hl=true&hl.snippets=10&hl.fl=textdata&hl.fragsize=200&hl.simple.pre=<code>&hl.simple.post=</code>&hl.usePhraseHighlighter=true&q.op=AND';
    if (req.query.dataset == 'oa'){
      //  SEARCH_URL += '&fl=appid,action_type,filename,minread,id,textdata';
    }else if (req.query.dataset == 'ptab'){
	    var ptab = true;
            //add query fields here later for ptab
   }

    // Debug for logs
    console.log(SEARCH_URL);

    var body;
    if (typeof req.query.q !== 'undefined') {
        unirest.get(SEARCH_URL).end(function (response) {
            if (typeof response.body !== 'undefined') {
                body = JSON.parse(response.body);
            }
            if (body && typeof body.response !== 'undefined' && typeof body.response.docs !== 'undefined') {
                res.render('newview', {
                    result:body.response.docs,
                    total:humanize.numberFormat(body.response.numFound,0),
                    pagein:paginate({totalItem:body.response.numFound, itemPerPage:20, currentPage:currentPage, url:'/newsearch',params: {q: q, dataset: req.query.dataset, fromdate: req.query.fromdate, todate: req.query.todate, art_unit: req.query.art_unit, documentcode: req.query.documentcode} }),
                    took:humanize.numberFormat(body.responseHeader.QTime,0 ),
                    highlighting:body.highlighting,
                    term:q,
                    ptab: ptab,
                    email: req.body.email,
                    todate: req.query.todate,
                    fromdate:req.query.fromdate,
                    artunit: req.query.art_unit,
                    documentcode: req.query.documentcode,
                    dataset: req.query.dataset
                });
            } else {
                res.render('newview', {
                    total:0,
                    pagein:'',
                    term:q,
                    ptab: ptab,
                    email: req.body.email,
                    message: validateMessage,
                    todate: req.query.todate,
                    fromdate:req.query.fromdate,
                    artunit: req.query.art_unit,
                    documentcode: req.query.documentcode,
                    dataset: req.query.dataset
                });
            }
        });
    } else {
        res.render('newview', {
            email: req.body.email,
        });
    }
};
