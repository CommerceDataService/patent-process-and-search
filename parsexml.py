#!/usr/bin/env python 3.5

#Author:        Sasan Bahadaran
#Date:          2/29/16
#Organization:  Commerce Data Service
#Description:   This script crawls the files directory and finds the metadata
#xml file for each set of pdf files.  It then gets the document id from
#the metadata and finds the associated extracted pdf text and adds it to the
#structure of the document, then transforms the document to json and saves it
#to a file.

import sys, json, xmltodict, os, logging, time, argparse, glob, requests
import dateutil.parser

from datetime import datetime


#change extension of file name to specified extension
def change_ext(fname, ext):
    seq = (os.path.splitext(fname)[0], ext)
    return '.'.join(seq)

#get field(date) and return in a proper iso format
def format_date(field,x):
    date = dateutil.parser.parse(x.pop(field))
    dateiso = date.isoformat()+'Z'
    return dateiso

#this function contains the code for parsing the xml file
#and writing the results out to a json file
def processFile(fname):
    type = os.path.splitext(fname)[1]
    doc = {}
    try:
        with open(os.path.abspath(fname)) as fd:
            if type == ".xml":
                fn = change_ext(fname,'json')
                doc = xmltodict.parse(fd.read())
            elif type == ".json":
                doc = json.loads(fd.read())
            #get document id from metadata xml file
            records = doc['main']['DATA_RECORD']
            for x in records:
                docid = x.get('DOCUMENT_IMAGE_ID',x.get('DOCUMENT_NM'))
                if type == ".xml":
                    txtfn = os.path.join(os.path.dirname(fn),'PDF_image',docid+'.txt')
                    if os.path.isfile(txtfn):
                        x['LAST_MODIFIED_TS'] = format_date('LAST_MODIFIED_TS',x)
                        x['PATENT_ISSUE_DT'] = format_date('PATENT_ISSUE_DT',x)
                        x['DECISION_MAILED_DT'] = format_date('DECISION_MAILED_DT',x)
                        x['PRE_GRANT_PUBLICATION_DT'] = format_date('PRE_GRANT_PUBLICATION_DT',x)
                        x['APPLICANT_PUB_AUTHORIZATION_DT'] = format_date('APPLICANT_PUB_AUTHORIZATION_DT',x)
                        x['appid'] = x.pop('BD_PATENT_APPLICATION_NO')
                        x['doc_date'] = x.pop('DOCUMENT_CREATE_DT')
                        with open(txtfn) as dr:
                            text = dr.read()
                            x['textdata'] = text
                    else:
                        logging.info("TXT file: "+docid+".txt  does not exist. JSON file creation skipped.")
                        return
                if (args.solr):
                    jsontext = json.dumps(x)
                    #Send content to Solr to update index
                    jsontext = '{"add":{ "doc":'+jsontext+',"boost":1.0,"overwrite":true, "commitWithin": 1000}}'
                    with open(os.path.join(os.path.dirname(fname),'jsoncomplete.txt'),'a+') as logfile:
                        logfile.seek(0)
                        if docid+"\n" in logfile:
                            logging.info("-- file: "+docid+"  already processed by Solr")
                            continue
                        else:
                            logging.info("-- Sending file: "+docid+" to Solr")
                            url = "http://54.208.116.77:8983/solr/ptab/update"
                            headers = {"Content-type" : "application/json"}
                            r = requests.post(url, data=jsontext, headers=headers)
                            rdict = json.loads(r.text)
                            status = rdict["responseHeader"]["status"] 
                            if status == 0:
                                logging.info("-- Solr update for file: "+docid+" complete")
                            else:
                                logging.info("-- Solr error for doc: "+docid+" error: "+', '.join("{!s}={!r}".format(k,v) for (k,v) in rdict.items()))
                            
            #transform output to json and save to file with same name
            if type == ".xml":
                with open(fn,'w') as outfile:
                    json.dump(doc,outfile)
                    logging.info("-- Processing of XML file and creation of json file complete")
                    
    except IOError as e:
        logging.error("I/O error({0}): {1}".format(e.errno,e.strerror))
    except:
        logging.error("Unexpected error:", sys.exc_info()[0])
        raise

#validate date
def validDate(s):
    try:
        datetime.strptime(s, "%Y%m%d")
        return s
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)

if __name__ == '__main__':
    scriptpath = os.path.dirname(os.path.abspath(__file__))

    #logging configuration
    logging.basicConfig(
                        filename='logs/parsexml-log-'+time.strftime('%Y%m%d'),
                        level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s -%(message)s',
                        datefmt='%Y%m%d %H:%M:%S'
                       )

    parser = argparse.ArgumentParser()
    parser.add_argument(
                        "-r",
                        "--reprocess",
                        required=False,
                        help="Reprocess file from a specific date - format YYYYMMDD",
                        nargs='*',
                        type=validDate
                       )
    parser.add_argument(
                        "-s",
                        "--solr",
                        required=False,
                        help="Pass this flag to skip Solr processing",
                        action='store_false'
                       )

    args = parser.parse_args()
    if args.reprocess:
        logging.info("Date arguments passed for reprocessing:"+", ".join(args.reprocess))
    if args.solr:
        logging.info("Solr processing for documents will be skipped: "+str(args.solr))
    logging.info("-- [JOB START]  ----------------")

    if args.reprocess:
       for date in args.reprocess:
           for dirname in glob.iglob(os.path.join(scriptpath,'files','PTAB*'+date)):
               #crawl through each main directory and find the metadata xml file
               for filename in glob.iglob(os.path.join(dirname,'*.xml'),recursive=True):
                   logging.info("-- Starting re-processing of file: "+filename)
                   processFile(filename)
    else:
        #crawl through each main directory and find the metadata xml file
        for filename in glob.iglob(os.path.join(scriptpath,'files','PTAB*/*.xml')):
            fn = change_ext(filename,'json')
            if not os.path.isfile(os.path.abspath(fn)):
                logging.info("-- Starting processing of file: "+filename)
                processFile(filename)
            else:
                logging.info("-- JSON file for file: "+filename+" already exists.")
                processFile(fn)

    logging.info("-- [JOB END] ----------------")
