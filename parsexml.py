#!/usr/bin/env python

#Author:        Sasan Bahadaran
#Date:          2/29/16
#Organization:  Commerce Data Service
#Description:   This script crawls the files directory and finds the metadata
#xml file for each set of pdf files.  It then gets the document id from
#the metadata and finds the associated extracted pdf text and adds it to the
#structure of the document, then transforms the document to json and saves it
#to a file.

import sys, json, xmltodict, os, logging, time, argparse, glob
from datetime import datetime

#this function contains the code for parsing the xml file
#and writing the results out to a json file
def processFile(fname,overwrite):
    try:
        with open(fname) as fd:
            fn = os.path.splitext(fname)[0]+'.json'
            doc = xmltodict.parse(fd.read())

            #get document id from metadata xml file
            for x in doc['main']['DATA_RECORD']:
                value = x.get('DOCUMENT_IMAGE_ID',x.get('DOCUMENT_NM'))
                with open(os.path.join(os.path.dirname(fn),'PDF_image',value+'.txt')) as dr:
                    text = dr.read()
                    x['DOCUMENT_TEXT'] = text
            #transform output to json and save to file with same name
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
    logging.basicConfig(filename='logs/parse-xml-log-'+time.strftime('%Y%m%d-%H%M%S'),\
    level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s\
    -%(message)s',datefmt='%Y%m%d %H:%M:%S')

    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--reprocess", required=False,\
    help="Reprocess file from a specific date - format YYYYMMDD",\
    nargs='*', type=validDate)
    args = parser.parse_args()
    if args.reprocess:
        logging.info("Date arguments passed for reprocessing:"+", ".join(args.reprocess))

    logging.info("-- [JOB START]  ----------------")
    logging.info("-- =============== Script starting ====================")

    if args.reprocess:
       for date in args.reprocess:
           for dirname in glob.iglob(os.path.join(scriptpath,'files','*'+date)):
               #crawl through each main directory and find the metadata xml file
               for filename in glob.iglob(os.path.join(dirname,'*.xml'),recursive=True):
                   logging.info("-- Starting re-processing of file: "+filename)
                   processFile(os.path.abspath(filename),True)
    else:
        #crawl through each main directory and find the metadata xml file
        for filename in glob.iglob(os.path.join(scriptpath,'files','**/*.xml')):
            if not os.path.isfile(os.path.join(os.path.splitext(os.path.abspath(filename))[0]+'.json')):
                logging.info("-- Starting processing of file: "+filename)
                processFile(os.path.abspath(filename),False)
            else:
                logging.info("-- JSON file for file: "+filename+" already exists")

    logging.info("-- =============== Script exiting ====================")
    logging.info("-- [JOB END] ----------------")
