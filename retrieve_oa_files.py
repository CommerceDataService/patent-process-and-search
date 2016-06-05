#!/usr/bin/env python 3.5

import sys, os, glob, shutil, logging, time, argparse, glob
from datetime import datetime

def getAppIDs(fname,series):
    try:
        with open(os.path.abspath(fname)) as fd:
            for line in fd:
                if line.startswith(series):
                    appids.append(line.strip("\n"))
        logging.info("-- Number of appids for this series: "+str(len(appids)))
    except IOError as e:
         logging.error('I/O error({0}): {1}'.format(e.errno,e.strerror))
    except:
         logging.error('Unexpected error:', sys.exc_info()[0])
         raise

def constructPath(appid):
    series = appid[:2]
    series2 = appid[2:5]
    series3 = appid[5:8]
    return os.path.join(oafilespath,series,series2,series3)

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
    appid = str(paramList[7])+str(paramList[8])+str(paramList[9])
    selparts = (filename,appid,paramList[11])
    newfname = os.path.join(scriptpath,'extractedfiles',series,'_'.join(selparts)+'.xml')
    return newfname

def copyFile(old,new):
    try:
        fpath, fname = os.path.split(new)
        if not os.path.isfile(new):
            shutil.copyfile(old,new)
            logging.info("-- File: "+fname+" written to directory: "+fpath)
        else:
            logging.info("-- File: "+fname+" already exists")
    except:
        logging.error('Unexpected error:', sys.exc_info()[0])
        raise

if __name__ == '__main__':
    scriptpath = os.path.dirname(os.path.abspath(__file__))
    pubidpath = 'files/OFFICEACTIONS/pair_app_ids.txt'
    #use this on pto machine
    #oafilespath = '\\s-mdw-isl-b02-smb.uspto.gov\BigData\PE2E-ELP\PATENT'
    oafilespath = os.path.join(scriptpath,'PE2E-ELP/PATENT')
    appids = []

    #logging configuration
    logging.basicConfig(
                        filename='logs/extract-files--log-'+time.strftime('%Y%m%d'),
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
                        '-z',
                        '--zipfiles',
                        required=False,
                        help='Pass this flag to create zip file from all extracted files at end of process',
                        action='store_true'
                       )
    args = parser.parse_args()
    logging.info("-- SCRIPT ARGUMENTS -------------")
    if args.series:
        logging.info("-- Series passed for processing: "+", ".join(args.series))
    logging.info("Skip Combine set to: "+str(args.zipfiles))

    logging.info("-- [JOB START]  ----------------")

    for series in args.series:
        logging.info("-- Processing series: "+series)
        getAppIDs(os.path.join(scriptpath,pubidpath),series)
        makeDirectory(os.path.join(scriptpath,'extractedfiles',series))
        for x in appids:
            seriesdirpath = constructPath(x)
            for filename in glob.iglob(os.path.join(seriesdirpath,'*','*','*','*','*.xml'),recursive=True):
                logging.info("-- Processing file: "+filename)
                filepath = os.path.dirname(filename)
                allparts = splitAll(filepath)
                newfname = constructFilename(filename,allparts)
                logging.info("-- New file name: "+newfname)
                copyFile(filename,newfname)
        del appids[:]
    logging.info("-- [JOB END] -------------------")
