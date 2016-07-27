#!/usr/bin/env python 3.5

#Author:        Sasan Bahadaran
#Date:          6/27/16
#Organization:  Commerce Data Service
#Description:   This script crawls specific directory structures of Office Action
#files, renames them with app ID and IFW number, parses the XML, combines the XML
#with PALM data from flat files, and gets the post date from a CMS RESTFUL service.
#It then transforms the resulting dictionary to JSON and sends it to Solr for indexing.

import sys, os,  shutil, logging, time, argparse, glob, json, requests, collections

from datetime import datetime
from lxml import etree
import pandas as pd

from s3_upload.s3_uploader_new import S3Uploader
from s3_upload.util import Util

#get public app IDs from app ID file
def getAppIDs(fname,series):
    try:
        with open(os.path.abspath(fname)) as fd:
            for line in fd:
                if line.startswith(series):
                    appids.append(line.strip())
        logging.info("-- Number of appids for this series: "+str(len(appids)))
    except IOError as e:
         logging.error('-- Get App IDs I/O error({0}): {1}'.format(e.errno,e.strerror))

#construct app ID file path from app ID
def constructPath(appid):
    fileurl = oafilespath+'\\'+appid[:2]+'\\'+appid[2:5]+'\\'+appid[5:8]
    return fileurl

#create directory if it does not exist
def makeDirectory(directory):
    if not os.path.isdir(directory):
        os.makedirs(directory)

#split path to get app ID
def splitAll(path):
    allparts = []
    while 1:
        parts = os.path.split(path)
        if parts[0] == path:  # sentinel for absolute paths
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path: # sentinel for relative paths
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])
    return allparts

#construct file name from app ID, ifw number, and original name
def constructFilename(fname,paramList):
    fpath,filename = os.path.split(fname)
    filename = os.path.splitext(filename)[0]
    filename = filename.replace(" ","_").replace("'","")
    selparts = (str(paramList[3])+str(paramList[4])+str(paramList[5]),str(paramList[7]),filename)
    newfname = os.path.join(scriptpath,'extractedfiles',series,'_'.join(selparts)+'.xml')
    return newfname

#copy extracted file to central directory
def copyFile(old,new):
    try:
        fpath, fname = os.path.split(new)
        if not os.path.isfile(new):
            shutil.copyfile(old,new)
            logging.info("-- File: "+fname+" written to directory: "+fpath)
            completeappids.append(currentapp)
        else:
            logging.info("-- File: "+fname+" already exists")
    except IOError as e:
         logging.error('-- Copy File I/O error({0}): {1}'.format(e.errno,e.strerror))

#write list of app ID's to specified log file
def writeLogs(logfname,idlist):
    try:
        with open(logfname,'a+') as logfile:
            for appid in idlist:
                logfile.write(appid+"\n")
        logging.info('-- Log entries for: '+logfname+' written to file')
    except IOError as e:
        logging.error('-- Write Log: '+logfname+' I/O error({0}): {1}'.format(e.errno,e.strerror))

#change extension of file name to specified extension
def changeExt(fname, ext):
    seq = (os.path.splitext(fname)[0], ext)
    return '.'.join(seq)

#get metadata and text from P tags in XML document
def getText(node):
    contents = ''
    if node.tag == '{urn:us:gov:doc:uspto:common}LI' and node.text is not None:
        contents += (node.get('{http://www.wipo.int/standards/XMLSchema/ST96/Common}liNumber')+' '+node.text +
                     ''.join(map(getText, node)) +
                     (node.tail or ''))
    #ignore data table text
    elif node.tag == '{urn:us:gov:doc:uspto:common}DataTable':
        return contents
    #ignore image paragraphs
    elif node.tag == '{http://www.wipo.int/standards/XMLSchema/ST96/Common}Image':
        return contents
    else:
        contents += ((node.text or '') +
                    ''.join(map(getText, node)) +
                    (node.tail or ''))
    return contents

#code for parsing XML file
def parseXML(fname):
    try:
        textdata = ''
        parser = etree.XMLParser(remove_pis=True)
        tree = etree.parse(fname, parser=parser)
        root = tree.getroot()
        namespaces = {'uspat':'urn:us:gov:doc:uspto:patent',
                      'uscom':'urn:us:gov:doc:uspto:common',
                      'com':'http://www.wipo.int/standards/XMLSchema/ST96/Common'}
        for item in root.xpath('//uspat:DocumentMetadata', namespaces=namespaces):
            doccontent['documentcode'] = item.find('uscom:DocumentCode', namespaces=namespaces).text
            doccontent['documentsourceidentifier'] = item.find('uscom:DocumentSourceIdentifier', namespaces=namespaces).text
            partyid = doccontent['partyidentifier'] = item.find('com:PartyIdentifier', namespaces=namespaces)
            if partyid is not None:
                doccontent['partyidentifier'] = partyid.text
            else:
                doccontent['partyidentifier'] = ''
            doccontent['groupartunitnumber'] = item.find('uscom:GroupArtUnitNumber', namespaces = namespaces).text
        for item in root.xpath('//uscom:P', namespaces=namespaces):
            textdata += getText(item)+'\n'
        doccontent['textdata'] = textdata
        return True
    except IOError as e:
        logging.error('XML Parse file: '+fname+' I/O error({0}): {1}'.format(e.errno,e.strerror))
        return False
    except etree.XMLSyntaxError:
        logging.error('-- Skipping invalid XML from file: '+fname)
        badfiles.append(fname)
        return False

#convert day-month-year to UTC timestamp
def convertToUTC(date,format):
    if date != '' and date != None:
        dt = datetime.strptime(date, format)
        dt = time.mktime(dt.timetuple())
    else:
        dt = ''
    return dt

def loadPALMdata():
    logging.info('-- Loading PALM data')
    dataframe =  pd.read_csv(os.path.join(palmfilespath, 'app'+series+'.csv'), encoding = 'latin-1')
    logging.info('-- PALM data loaded into dataframe')
    return dataframe

#code for extracting PALM data from PALM series file and combine with other elements from XML file
def getPALMData(fileappid):
    try:
        logging.info('-- Starting PALM data match process')
        values = df.loc[df['APPL_ID'] == float(fileappid)]
        if len(values.index) == 1:
            values = values.to_dict('list')
            doccontent['appl_id'] = str(values['APPL_ID'][0])
            doccontent['file_dt'] = convertToUTC(str(values['FILE_DT'][0]), '%d-%b-%y')
            doccontent['effective_filing_dt'] = convertToUTC(str(values['EFFECTIVE_FILING_DT'][0]), '%d-%b-%y')
            doccontent['inv_subj_matter_ty'] = str(values['INV_SUBJ_MATTER_TY'][0])
            doccontent['appl_ty'] = str(values['APPL_TY'][0])
            doccontent['dn_examiner_no'] = str(values['DN_EXAMINER_NO'][0]).strip()
            doccontent['dn_dw_dn_gau_cd'] = str(values['DN_DW_DN_GAU_CD'][0])
            doccontent['dn_pto_art_class_no'] = str(values['DN_PTO_ART_CLASS_NO'][0])
            doccontent['dn_pto_art_subclass_no'] = str(values['DN_PTO_ART_SUBCLASS_NO'][0])
            doccontent['confirm_no'] = str(values['CONFIRM_NO'][0])
            doccontent['dn_intppty_cust_no'] = str(values['DN_INTPPTY_CUST_NO'][0])
            doccontent['atty_dkt_no'] = str(values['ATTY_DKT_NO'][0])
            doccontent['dn_nsrd_curr_loc_cd'] = str(values['DN_NSRD_CURR_LOC_CD'][0]).strip()
            doccontent['dn_nsrd_curr_loc_dt'] = convertToUTC(str(values['DN_NSRD_CURR_LOC_DT'][0]), '%d-%b-%y')
            doccontent['app_status_no'] = str(values['APP_STATUS_NO'][0])
            doccontent['app_status_dt'] = convertToUTC(str(values['APP_STATUS_DT'][0]), '%d-%b-%y')
            doccontent['wipo_pub_no'] = str(values['WIPO_PUB_NO'][0])
            doccontent['patent_no'] = str(values['PATENT_NO'][0])
            doccontent['patent_issue_dt'] = convertToUTC(str(values['PATENT_ISSUE_DT'][0]), '%d-%b-%y')
            doccontent['abandon_dt'] = convertToUTC(str(values['ABANDON_DT'][0]), '%d-%b-%y')
            doccontent['disposal_type'] = str(values['DISPOSAL_TYPE'][0])
            doccontent['se_in'] = str(values['SE_IN'][0])
            doccontent['pct_no'] = str(values['PCT_NO'][0]).strip()
            doccontent['invn_ttl_tx'] = str(values['INVN_TTL_TX'][0])
            doccontent['aia_in'] = str(values['AIA_IN'][0])
            doccontent['continuity_type'] = str(values['CONTINUITY_TYPE'][0]).strip()
            doccontent['frgn_priority_clm'] = str(values['FRGN_PRIORITY_CLM'][0])
            doccontent['usc_119_met'] = str(values['USC_119_MET'][0])
            doccontent['fig_qt'] = str(values['FIG_QT'][0])
            doccontent['indp_claim_qt'] = str(values['INDP_CLAIM_QT'][0])
            doccontent['efctv_claims_qt'] = str(values['EFCTV_CLAIMS_QT'][0])
            logging.info('-- PALM data written to doccontent dictionary')
            return True
        else:
            logging.error('-- Application ID: '+fileappid+' not found in PALM data')
            notfoundPALM.append(fileappid)
            return False
    except IOError as e:
        logging.error('PALM Extract file: '+fileappid+' I/O error({0}): {1}'.format(e.errno,e.strerror))
        return False

#get official application doc date
def getDocDate(appid, ifwnum):
    try:
        params = [{"businessUnitId": appid,
              "documentId": ifwnum}]
        headers = {'Content-type': 'application/json'}
        response = requests.post(cmsURL, json=params, headers=headers)
        r = response.json()
        if 'httpStatus' in r:
            doc_date = ''
            logging.info('-- App ID: '+appid+', IFW#: '+ifwnum+' not found from CMS service')
            notfoundCMS.append(appid+', '+ifwnum)
        elif 'officialDocumentDate' in r[0]:
            doc_date = convertToUTC(r[0]['officialDocumentDate'], '%Y-%m-%d')
        else:
            logging.info('-- CMS RESTFUL call neither contained an error or the doc date')
            doc_date = ''
        doccontent['doc_date'] = doc_date
        return True
    except requests.exceptions.RequestException as e:
        logging.error('-- CMS Restful error for: '+appid+', '+ifwnum+', error: '+e)
        notfoundCMS.append(appid+', '+ifwnum)
        return False

#write dictionary to JSON file
def writeToJSON(fname):
    try:
        with open(fname,'w') as outfile:
            json.dump(doccontent,outfile)
            logging.info('-- File written to : '+fname)
            return True
    except IOError as e:
        logging.error('Write to JSON: '+fname+' I/O error({0}): {1}'.format(e.errno,e.strerror))
        return False

#read JSON file and set up for sending to Solr
def readJSON(fname):
    try:
        fpath,filename = os.path.split(fname)
        docid = filename.split('_')[0]+', '+filename.split('_')[1]
        with open(fname, 'r') as fd:
            jsontext = fd.read().replace('\n', '')
            with open(os.path.join(os.path.dirname(fname), 'solrComplete.log'), 'a+') as logfile:
                logfile.seek(0)
                if docid+'\n' in logfile:
                    logging.info('-- File: '+docid+' already processed by Solr')
                else:
                    logging.info('-- Sending file: '+fname+' to Solr')
                    response = sendToSolr('oadata_2_shard1_replica1', jsontext)
                    r = response.json()
                    status = r['responseHeader']['status']
                    if status == 0:
                        logfile.write(docid+"\n")
                        logging.info('-- Solr update for file: '+docid+' complete')
                        return True
                    else:
                        logging.info('-- Solr error for doc: '+docid+' error: '+\
                        ', '.join("{!s}={!r}".format(k,v) for (k,v) in r.items()))
                        return False
    except IOError as e:
        logging.error('Read JSON file: '+fname+' I/O error({0}): {1}'.format(e.errno,e.strerror))
        return False
    except:
        logging.error('Unexpected error:', sys.exc_info()[0])
        raise
        return False

#read JSON file and set up for sending to Solr
def postFromS3ToSOLR(obj):
    try:
        log_dir_path = os.path.join("logs", "solr_upload", Util.log_directory(obj.key))
        logging.info("Log dir for file " + log_dir_path )
        os.makedirs(log_dir_path, exist_ok=True)

        docid = Util.doc_id(obj.key)
        objdata = obj.get()
        jsontext = objdata['Body'].read()

        jsontext = Util.reprocess_document(jsontext, obj.key)


        with open(os.path.join(log_dir_path  , 'solrComplete.log'), 'a+') as logfile:
                logfile.seek(0)
                if docid+'\n' in logfile:
                    logging.info('-- File: '+docid+' already processed by Solr')
                else:
                    logging.info('-- Sending file: '+obj.key+' to Solr')
                    response = sendToSolr('oadata_3_shard1_replica3', jsontext)
                    r = response.json()
                    status = r['responseHeader']['status']
                    if status == 0:
                        logfile.write(docid+"\n")
                        logging.info('-- Solr update for file: '+docid+' complete')
                        return True
                    else:
                        logging.info('-- Solr error for doc: '+docid+' error: '+ \
                        ', '.join("{!s}={!r}".format(k,v) for (k,v) in r.items()))
                        return False
    except IOError as e:
        logging.error('Read JSON file: '+ obj.key +' I/O error({0}): {1}'.format(e.errno,e.strerror))
        return False
    except:
        logging.error('Unexpected error:', sys.exc_info()[0])
        raise

#send document to Solr for indexin
def sendToSolr(core, json):
    try:
        jsontext = b'{"add":{ "doc":'+json+b',"boost":1.0,"overwrite":true, "commitWithin": 1000}}'
        url = os.path.join(solrURL,"solr",core,"update")
        headers = {"Content-type" : "application/json"}
        return requests.post(url, data=jsontext, headers=headers)
    except requests.exceptions.RequestException as e:
        logging.error('-- Solr indexing error: {}'.format(e))

if __name__ == '__main__':
    scriptpath = os.path.dirname(os.path.abspath(__file__))
    pubidfname = 'pair_app_ids.txt'
    oafilespath = '\\\\s-mdw-isl-b02-smb.uspto.gov\\BigData\\PE2E-ELP\\PATENT'
    palmfilespath = '\\\\nsx-orgshares\\CIO-OCIO\\BDR_Access\\PALM'
    cmsURL = 'http://p-elp-services.uspto.gov/cmsservice/pto/PATENT/documentMetadataByAccess'
    solrURL = 'http://52.90.109.169:8983'
    appids = []
    completeappids = []
    notfoundappids = []
    nofileappids = []
    notfoundPALM = []
    notfoundCMS = [] #records appid and ifw number
    badfiles = []
    currentapp = ''
    numoffileswritten = 0

    doccontent = collections.OrderedDict()

    #logging configuration
    logging.basicConfig(
                        filename='logs/extract-files-log-'+time.strftime('%Y%m%d')+'.txt',
                        level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s -%(message)s',
                        datefmt='%Y%m%d %H:%M:%S'
                       )
    parser = argparse.ArgumentParser()
    parser.add_argument(
                        '-s',
                        '--series',
                        required=True,
                        help='Specify series to process - format ## (separate each additional series with space)',
                        nargs='*',
                        type=str
                       )
    parser.add_argument(
                        '-e',
                        '--skipextraction',
                        required=False,
                        help='Pass this flag to skip File extraction',
                        action="store_true",
                        default = False
                       )
    parser.add_argument(
                        '-p',
                        '--skipparsing',
                        required=False,
                        help='Pass this flag to skip File parsing',
                        action="store_true",
                        default=False
                       )
    parser.add_argument(
                        '-i',
                        '--skipsolr',
                        required=False,
                        help='Pass this flag to skip Solr indexing',
                        action="store_true",
                        default=False
                       )
    parser.add_argument(
                        '-3',
                        '--s3tosolr',
                        required=False,
                        help='Pass this flag to send from S3 to SOLR',
                        action="store_true",
                        default=False
                       )
    args = parser.parse_args()
    logging.info("-- SCRIPT ARGUMENTS ------------")
    if args.series:
        logging.info("-- Series passed for processing: "+", ".join(args.series))
    logging.info("-- Skip Extraction flag set to: "+str(args.skipextraction))
    logging.info("-- Skip Parsing flag set to: "+str(args.skipparsing))
    logging.info("-- Skip Solr flag set to: "+str(args.skipsolr))
    logging.info("-- [JOB START]  ----------------")

    for series in args.series:
        seriespath = os.path.join(scriptpath,'extractedfiles', series)
        if not args.skipextraction:
            logging.info("-- Processing series: "+series)
            getAppIDs(os.path.join(scriptpath, 'files', 'PAIR', pubidfname), series)
            makeDirectory(os.path.join(scriptpath, 'extractedfiles', series))
            for x in appids:
                try:
                    currentapp = x
                    seriesdirpath = constructPath(x)
                    if os.path.isdir(seriesdirpath):
                        filenotfound = False
                        dirfiles = {}
                        for name in glob.glob(os.path.join(seriesdirpath, 'OA2XML', '*', 'xml', '1.0', '*')):
                            if os.path.isdir(name):
                                filenotfound = True
                                logging.info('-- No XML file found for path: '+name)
                            elif os.path.splitext(name)[1] == '.xml':
                                allparts = splitAll(os.path.dirname(name))
                                newfname = constructFilename(name, allparts)
                                logging.info("-- New file name: "+newfname)
                                dirfiles[name] = newfname
                        if filenotfound == False:
                            #for each file, run copy
                            for k, v in dirfiles.items():
                                copyFile(k, v)
                        else:
                            logging.info('-- One of the files for app ID: '+currentapp+' not found')
                            nofileappids.append(currentapp)
                    else:
                        logging.info("-- App ID: "+currentapp+" not found")
                        notfoundappids.append(currentapp)
                    currentapp = ''
                except IOError as e:
                    logging.error('-- Extraction file: '+' I/O error({0}): {1}'.format(e.errno,e.strerror))
                except:
                    logging.error('-- Unexpected error:', sys.exc_info()[0])
                    raise
            writeLogs(os.path.join(seriespath,'appcomplete.log'),completeappids)
            writeLogs(os.path.join(seriespath,'appnotfound.log'),notfoundappids)
            writeLogs(os.path.join(seriespath,'nofilefound.log'),nofileappids)
            #empty lists
            del appids[:]
            del completeappids[:]
            del notfoundappids[:]
            del nofileappids[:]
        if not args.skipparsing:
            df = loadPALMdata()
            for filename in glob.glob(os.path.join(seriespath, '*.xml')):
                logging.info('-- Start Processing file: '+filename)
                fname = os.path.join(seriespath, filename)
                fn = changeExt(fname, 'json')
                if not os.path.isfile(fn):
                    fileappid = (os.path.basename(filename)).split('_')[0]
                    ifwnum = (os.path.basename(filename)).split('_')[1]
                    #type set to oa for office actions
                    doccontent['type'] = 'oa'
                    doccontent['appid'] = fileappid
                    #IFW number for action
                    doccontent['ifwnumber'] = ifwnum
                    if parseXML(fname):
                        if getPALMData(fileappid):
                            if getDocDate(fileappid, ifwnum):
                                if writeToJSON(fn):
                                    numoffileswritten += 1
                                    logging.info('-- {} - Complete processing for file: {}'.format(numoffileswritten,fn))
                                else:
                                    logging.error('-- write to JSON for file: '+filename+' failed')
                            else:
                                logging.error('-- Retrieval of Doc Date for file: '+filename+' failed')
                        else:
                            logging.error('-- Extraction of PALM data for file: '+filename+' failed')
                    else:
                        logging.error('-- Parsing of file: '+filename+' failed')
                else:
                    logging.info('File: '+fn+' already exists')
                    if not args.skipsolr:
                        logging.info('-- Reading JSON file: '+fn)

                doccontent.clear()
            writeLogs(os.path.join(seriespath,'notfoundPALM.log'),notfoundPALM)
            writeLogs(os.path.join(seriespath,'notfoundCMS.log'),notfoundCMS)
            writeLogs(os.path.join(seriespath,'badfiles.log'),badfiles)
            del notfoundPALM[:]
            del notfoundCMS[:]
            del badfiles[:]
        if not args.skipsolr:
            filecounter = 0
            for filename in glob.glob(os.path.join(seriespath,'*.json')):
                logging.info('-- Reading JSON file: '+filename)
                if filecounter < 10001:
                    if readJSON(filename):
                        filecounter += 1
                else:
                    logging.info('Total number of files processed: '+filecounter)
        if not args.s3tosolr:
            logging.info("From S3 to SOLR : Series [" + series + "]")

            uploader = S3Uploader('uspto-bdr')
            files = uploader.get_file_list(series + "/" + "130000")
            for x in files:
                logging.info( "Uploading " + x.key )
                postFromS3ToSOLR(x)


    logging.info("-- [JOB END] -------------------")
