#!/usr/bin/env python 3.5

import sys, os, glob, shutil, logging, time, argparse, glob
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
    args = parser.parse_args()
    logging.info("-- SCRIPT ARGUMENTS ------------")
    if args.series:
        logging.info("-- Series passed for processing: "+", ".join(args.series))

    logging.info("-- [JOB START]  ----------------")

    for series in args.series:
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

    logging.info("-- [JOB END] -------------------")
