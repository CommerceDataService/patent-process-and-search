#!/usr/bin/env python 3.5

import sys, os, glob, shutil, logging, time, argparse, glob, xmltodict
from datetime import datetime

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

def constructPath(appid):
    series = appid[:2]
    series2 = appid[2:5]
    series3 = appid[5:8]
    fileurl = oafilespath+'\\'+series+'\\'+series2+'\\'+series3
    return fileurl

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

# def writeNotFoundApps(logfname):
#     try:
#         with open(logfname,'a+') as logfile:
#             for appid in notfoundappids:
#                 logfile.write(appid+"\n")
#     except IOError as e:
#         logging.error('I/O error({0}): {1}'.format(e.errno,e.strerror))

# def loadProcessedApps(logfname,type):
#     try:
#         if os.path.isfile(logfname):
#             prevcompappids = [line.strip() for line in open(logfname,'r')]
#     except IOError as e:
#         logging.error('I/O error({0}): {1}'.format(e.errno,e.strerror))
#         raise
#
# def removeProcessedApps(logfname):
#     if len(prevcompappids) > 0:
#         #get diff between appids and prevcompappids
#     if len(notfoundappids) > 0:
#         #get diff between appids and notfoundappids

#change extension of file name to specified extension
def changeExt(fname, ext):
    seq = (os.path.splitext(fname)[0], ext)
    return '.'.join(seq)

def mutate(iterable):
    ptag = False
    btag = False
    if isinstance(iterable, list):
        indexed_list = enumerate(iterable)
        print("list")
    elif isinstance(iterable, dict):
        indexed_list = iterable.items()
        print("dict")
    else:
        indexed_list = iterable
        print("else")
    for k,item in indexed_list:
        if isinstance(item, list):
            if k == 'uscom:P':
                print("P TAG: "+item)
        if isinstance(item, dict):
            print("mutate-item")
            mutate(item)
        #if isinstance(item, dict) or isinstance(item, list) and k == 'uscom:P':
        #    print("mutate-item")
            #if k == 'uscom:P':
            #    print("P tag")
            #    ptag = True
            #elif k == 'com:B':
            #    print("B tag")
            #    btag = True
            #print(str(k))
            mutate(item)
        else:
            if item is not None:
                
                 print("else k: "+str(k)+", v: "+str(item))

#this function contains the code for parsing the xml file
#and writing the results out to a json file
def parseXML(fname):
    doccontent = {}
    try:
        fn = changeExt(fname, 'json')
        if not os.path.isfile(fn):
            with open(fname) as fd:
                logging.info("-- Beginning read of file")
                doc = xmltodict.parse(fd.read())
                logging.info("-- End of reading file and converting to dictionary")
                #print(doc)
                #for k,v in doc['uspat:OutgoingDocument']['uspat:DocumentMetadata'].items():
                #    if (k == 'uscom:DocumentCode'):
                #        doccontent['documentcode'] = v
                #    elif (k == 'uscom:DocumentSourceIdentifier'):
                #        doccontent['documentsourceidentifier'] = v
                #    elif (k == 'com:PartyIdentifier'):
                #        doccontent['partyidentifier'] = v
                #    elif (k == 'uscom:GroupArtUnitNumber'):
                #        doccontent['groupartunitnumber'] = v
                #    elif (k == 'uscom:ExaminationProgramCode'):
                #        doccontent['examinationprogramcode'] = v
                #    elif (k == 'uscom:AccessLevelCategory'):
                #        doccontent['accesslevelcategory'] = v
                    #for y in doc['uspat:OutgoingDocument']:
                for text in doc['uspat:OutgoingDocument']['uscom:FormParagraph']['uscom:P']:
                    print("PARAGRAPH*************")
                    mutate(text)
                    #for k,v in text['uscom:P'].items():

                   #     print("k: "+k+", v: "+v)
                        #mutate(y)

                        #print("{} {}".format(k, v))
                    #for y in x['uscom:DocumentCode'].items():
                    #    print(y)
                    #doccode = x['uscom:DocumentCode']
                    #print(doccode)
                    #doccontent.append(x['DocumentCode'] = x.pop('uscom:DocumentCode'))
                    #print(doccontent)


                #for k,v in doc['uspat:OutgoingDocument']['uspat:DocumentMetadata'].items():
                #        if (k == 'uscom:DocumentCode'):
                #            print(v)
                            #doccontent.append(d
                        #if isinstance(v,dict):
                        #    print("TRUE")
                        #    print(v)
                        #else:
                        #    print("FALSE")
                        #    print("{0} : {1}".format(k, v))
                    #for key,value in x.items():
                    #    print("key: "+key+", value: "+value)
                        #doccode = x['uscom:DocumentCode']
                        #print("doc code: "+str(doccode))


    except IOError as e:
        logging.error('I/O error({0}): {1}'.format(e.errno.e.strerror))
        raise

if __name__ == '__main__':
    scriptpath = os.path.dirname(os.path.abspath(__file__))
    pubidfname = 'pair_app_ids.txt'
    oafilespath = '\\\\s-mdw-isl-b02-smb.uspto.gov\\BigData\\PE2E-ELP\\PATENT'
    appids = []
    completeappids = []
    notfoundappids = []
    nofileappids = []
    #prevcompappids = []
    currentapp = ''

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
        if not args.skipextraction:
            logging.info("-- Processing series: "+series)
            seriespath = os.path.join(scriptpath,'extractedfiles',series)
            getAppIDs(os.path.join(scriptpath,pubidfname),series)
            #loadProcessedApps(logfile)
            #removeProcessedApps(logfile)
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
                    logging.error(-- 'I/O error({0}): {1}'.format(e.errno,e.strerror))
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
            parseXML(os.path.join(scriptpath,'extractedfiles','14','Final_Rejection_14092037_WLKDS109387.xml'))
    logging.info("-- [JOB END] -------------------")
