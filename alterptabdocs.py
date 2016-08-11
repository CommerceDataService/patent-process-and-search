#!/usr/bin/env python 3.5

#Author:        Sasan Bahadaran
#Date:          8/11/16
#Organization:  Commerce Data Service
#Description:   This script alters existing JSON files created from PTAB data to format
#fields properly and add any fields necessary for the new Solr architecture

import sys, json, os, glob, time
import dateutil.parser

from datetime import datetime

#get field(date) and return in UTC format
def convertToUTC(x, field):
    date = str(x.pop(field))
    if date != '0001-01-01T00:00:00Z':
        date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
        date = time.mktime(date.timetuple())
    else:
        date = 978325200.0
    return date

def convertToReadableDate(date):
    date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
    date = datetime.strftime(date, '%m/%d/%Y')
    return date

#this function contains the code for altering the existing
#JSON structure to format date fields, add type field, and
#add truncated text field
def alterJSON(fname):
    try:
        with open(os.path.abspath(fname)) as fd:
            print("--Reading file: "+fname)
            doc = json.loads(fd.read())
            records = doc['main']['DATA_RECORD']
            for x in records:
                last_modified_ts = x['LAST_MODIFIED_TS']
                x['LAST_MODIFIED_TS'] = convertToUTC(x, 'LAST_MODIFIED_TS')
                x['LAST_MODIFIED_TS_frmt'] = convertToReadableDate(last_modified_ts)
                x['PATENT_ISSUE_DT_frmt'] = convertToReadableDate(x['PATENT_ISSUE_DT'])
                x['PATENT_ISSUE_DT'] = convertToUTC(x, 'PATENT_ISSUE_DT')
                x['DECISION_MAILED_DT_frmt'] = convertToReadableDate(x['DECISION_MAILED_DT'])
                x['DECISION_MAILED_DT'] = convertToUTC(x, 'DECISION_MAILED_DT')
                x['PRE_GRANT_PUBLICATION_DT_frmt'] = convertToReadableDate(x['PRE_GRANT_PUBLICATION_DT'])
                x['PRE_GRANT_PUBLICATION_DT'] = convertToUTC(x, 'PRE_GRANT_PUBLICATION_DT')
                x['APPLICANT_PUB_AUTHORIZATION_DT_frmt'] = convertToReadableDate(x['APPLICANT_PUB_AUTHORIZATION_DT'])
                x['APPLICANT_PUB_AUTHORIZATION_DT'] = convertToUTC(x, 'APPLICANT_PUB_AUTHORIZATION_DT')
                x['doc_date_frmt'] = convertToReadableDate(x['doc_date'])
                x['doc_date'] = convertToUTC(x, 'doc_date')
                x['type'] = 'ptab'
                x['textdata_frmt'] = x['textdata'][:32000]

            #transform output to json and save to file with same name
            with open(fname,'w') as outfile:
                json.dump(doc,outfile)
                print("--Alteration of file complete")
    except IOError as e:
        print("I/O error({0}): {1}".format(e.errno,e.strerror))
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise

if __name__ == '__main__':
    scriptpath = os.path.dirname(os.path.abspath(__file__))

    for filename in glob.iglob(os.path.join(scriptpath,'files/PTAB','PTAB*/*.json')):
        alterJSON(filename)
