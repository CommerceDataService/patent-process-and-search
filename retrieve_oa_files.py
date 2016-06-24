#!/usr/bin/env python 3.5

import sys, os, glob, shutil, logging, time, argparse, glob, xmltodict, json, csv, requests
from datetime import datetime
from lxml import etree

def getAppIDs(fname,series):
    try:
        with open(os.path.abspath(fname)) as fd:
            for line in fd:
                if line.startswith(series):
                    appids.append(line.strip())
        logging.info("-- Number of appids for this series: "+str(len(appids)))
    except IOError as e:
         logging.error('-- I/O error({0}): {1}'.format(e.errno,e.strerror))
    except:
         logging.error('-- Unexpected error:', sys.exc_info()[0])
         raise

#construct app ID file path from app ID
def constructPath(appid):
    fileurl = oafilespath+'\\'+appid[:2]+'\\'+appid[2:5]+'\\'+appid[5:8]
    return fileurl

#create directory if it does not exist
def makeDirectory(directory):
    if not os.path.isdir(directory):
        os.makedirs(directory)


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

def constructFilename(fname,paramList):
    fpath,filename = os.path.split(fname)
    filename = os.path.splitext(filename)[0]
    filename = filename.replace(" ","_").replace("'","")
    selparts = (str(paramList[3])+str(paramList[4])+str(paramList[5]),str(paramList[7]),filename)
    newfname = os.path.join(scriptpath,'extractedfiles',series,'_'.join(selparts)+'.xml')
    print("new filename: "+newfname)
    return newfname

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
         logging.error('-- I/O error({0}): {1}'.format(e.errno,e.strerror))
    except:
        logging.error('-- Unexpected error:', sys.exc_info()[0])
        raise

def writeLogs(logfname,idlist):
    try:
        with open(logfname,'a+') as logfile:
            for appid in idlist:
                logfile.write(appid+"\n")
    except IOError as e:
        logging.error('-- I/O error({0}): {1}'.format(e.errno,e.strerror))

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
    elif node.tag == '{urn:us:gov:doc:uspto:common}DataTable':
        return contents
    else:
        contents += ((node.text or '') +
                    ''.join(map(getText, node)) +
                    (node.tail or ''))
    return contents

#write dictionary to JSON file
def writeToJSON(fname):
    try:
        with open(fname,'w') as outfile:
            json.dump(doccontent,outfile)
            logging.info("-- Processing of XML file complete")
    except IOError as e:
        logging.error('I/O error({0}): {1}'.format(e.errno.e.strerror))
        raise

#code for parsing XML file
def parseXML(fname):
    try:
        textdata = ''
        fn = changeExt(fname, 'json')
        if not os.path.isfile(fn):
            parser = etree.XMLParser(remove_pis=True)
            tree = etree.parse(fname, parser=parser)
            root = tree.getroot()
            namespaces = {'uspat':'urn:us:gov:doc:uspto:patent',
                          'uscom':'urn:us:gov:doc:uspto:common',
                          'com':'http://www.wipo.int/standards/XMLSchema/ST96/Common'}

            for item in root.xpath('//uspat:DocumentMetadata', namespaces=namespaces):
                doccontent['documentcode'] = item.find('uscom:DocumentCode', namespaces=namespaces).text
                doccontent['documentsourceidentifier'] = item.find('uscom:DocumentSourceIdentifier', namespaces=namespaces).text
                doccontent['partyidentifier'] = item.find('com:PartyIdentifier', namespaces=namespaces).text
                doccontent['groupartunitnumber'] = item.find('uscom:GroupArtUnitNumber', namespaces = namespaces).text

            for item in root.xpath('//uscom:P',namespaces=namespaces):
                textdata += getText(item)+'\n'

            doccontent['textdata'] = textdata
        else:
            logging.info('File: '+fname+' already exists')
    except IOError as e:
        logging.error('I/O error({0}): {1}'.format(e.errno.e.strerror))
        raise

#code for extracting PALM data from PALM series file and combine with other elements from XML file
def extractPALMData(appid):
    try:
        with open(os.path.join(scriptpath,'files','OFFICEACTIONS','PALM_extract.dsv'), 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter='|',quotechar='\"')
            next(reader, None)  # skip the headers
            for row in reader:
                match = row[0]
                if match == appid:
                    print(row)
                    doccontent['appl_id'] = row[0].strip()
                    doccontent['file_dt'] = row[1].strip()
                    doccontent['effective_filing_dt'] = row[2].strip()
                    doccontent['inv_subj_matter_ty'] = row[3].strip()
                    doccontent['appl_ty'] = row[4].strip()
                    doccontent['dn_examiner_no'] = row[5].strip()
                    doccontent['dn_dw_gau_cd'] = row[6].strip()
                    doccontent['dn_pto_art_class_no'] = row[7].strip()
                    doccontent['dn_pto_art_subclass_no'] = row[8].strip()
                    doccontent['confirm_no'] = row[9].strip()
                    doccontent['dn_intppty_cust_no'] = row[10].strip()
                    doccontent['atty_dkt_no'] = row[11].strip()
                    doccontent['dn_nsrd_curr_loc_cd'] = row[12].strip()
                    doccontent['dn_nsrd_curr_loc_dt'] = row[13].strip()
                    doccontent['app_status_no'] = row[14].strip()
                    doccontent['app_status_dt'] = row[15].strip()
                    doccontent['wipo_pub_no'] = row[16].strip()
                    doccontent['patent_no'] = row[17].strip()
                    doccontent['patent_issue_dt'] = row[18].strip()
                    doccontent['abandon_dt'] = row[19].strip()
                    doccontent['disposal_type'] = row[20].strip()
                    doccontent['se_in'] = row[21].strip()
                    doccontent['pct_no'] = row[22].strip()
                    doccontent['invn_ttl_tx'] = row[23].strip()
                    doccontent['aia_in'] = row[24].strip()
                    doccontent['continuity_type'] = row[25].strip()
                    doccontent['frgn_priority_clm'] = row[26].strip()
                    doccontent['usc_119_met'] = row[27].strip()
                    doccontent['fig_qt'] = row[28].strip()
                    doccontent['indp_claim_qt'] = row[29].strip()
                    doccontent['efctv_claims_qt'] = row[30].strip()
                    return True
            else:
                logging.error('-- Application ID: '+appid+' not found in PALM data')
                notfoundPALM.append(appid)
                return False
    except IOError as e:
        logging.error('I/O error({0}): {1}'.format(e.errno.e.strerror))
        return False
#get official application doc date
def getDocDate(appid):
    try:
        url = 'http://pelp-services-eap-0.dev.uspto.gov:8080/cmsservice/api/#/'
        #appid?
        response = requests.get(url, data=data)
    requests.exceptions.RequestException as e:
        logging.error('-- CMS Restful error: '+e)

if __name__ == '__main__':
    scriptpath = os.path.dirname(os.path.abspath(__file__))
    pubidfname = 'pair_app_ids.txt'
    oafilespath = '\\\\s-mdw-isl-b02-smb.uspto.gov\\BigData\\PE2E-ELP\\PATENT'
    appids = []
    completeappids = []
    notfoundappids = []
    nofileappids = []
    notfoundPALM = []
    notfoundCMS = []
    currentapp = ''
    doccontent = {}

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
                        action='store_true'
                       )
    args = parser.parse_args()
    logging.info("-- SCRIPT ARGUMENTS ------------")
    if args.series:
        logging.info("-- Series passed for processing: "+", ".join(args.series))
    logging.info("-- Skip Extraction flag set to: "+str(args.skipextraction))
    logging.info("-- [JOB START]  ----------------")

    for series in args.series:
        seriespath = os.path.join(scriptpath,'extractedfiles',series)
        if not args.skipextraction:
            logging.info("-- Processing series: "+series)
            getAppIDs(os.path.join(scriptpath,pubidfname),series)
            makeDirectory(os.path.join(scriptpath,'extractedfiles',series))
            for x in appids:
                try:
                    currentapp = x
                    seriesdirpath = constructPath(x)
                    if os.path.isdir(seriesdirpath):
                        for name in glob.glob(seriesdirpath+'\\OA2XML\\*\\xml\\1.0\\*'):
                            print(name)
                            if os.path.isdir(name):
                                nofileappids.append(currentapp)
                                logging.info("-- No XML file present for path: "+name)
                            elif os.path.splitext(name)[1] == '.xml':
                                allparts = splitAll(os.path.dirname(name))
                                newfname = constructFilename(name,allparts)
                                logging.info("-- New file name: "+newfname)
                                copyFile(name,newfname)
                    else:
                        print("in else: "+currentapp)
                        logging.info("-- App ID: "+currentapp+" not found")
                        notfoundappids.append(currentapp)
                    currentapp = ''
                except IOError as e:
                    logging.error('-- I/O error({0}): {1}'.format(e.errno,e.strerror))
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
        else:
            #hard-coded for testing.  Needs to be changed!
            #search seriespath for files, for each file, process
            filename = '14092037_WLKDS109837_Final_Rejection.xml'
            logging.info('-- Processing file: '+filename)
            fname = os.path.join(seriespath, filename)
            fileappid = filename.split('_')[0]
            doccontent['type'] = 'oa'
            doccontent['appid'] = fileappid
            
            if parseXML(fname):
                fn = changeExt(fname, 'json')
                if extractPALMData(fileappid):
                    if getDocDate(fileappid):
                            writeToJSON(fn)
                            logging.info('-- Processing of file: '+filename+' is complete')
                    else:
                        logging.error('-- Retrieval of Doc Date for file: '+filename+' failed')
                else:
                    logging.error('-- Extraction of PALM data for file: '+filename+' failed')
            else:
                logging.error('-- Parsing of file: '+filename+' failed')
            doccontent.clear()
    logging.info("-- [JOB END] -------------------")
