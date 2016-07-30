#!/usr/bin/env python 3.5

#Author:        Sasan Bahadaran
#Date:          7/30/16
#Organization:  Commerce Data Service
#Description:   This script crawls the directory of public pair files, extracts all
#application ID's from each file, stores it in a list, sorts it, and then writes it
#to a file for further use

import json, glob, os, collections, time, logging, argparse

def extractIDs(fname):
    try:
        fpath,filename = os.path.split(fname)
        logging.info('-- Processing file: '+filename)
        with open(fname, 'r') as fd:
            data = json.load(fd)
            apps = data['PatentBulkData']
            for app in apps:
                appid = app['applicationDataOrProsecutionHistoryDataOrPatentTermData'][0]['applicationNumberText']['value']
                publicappids.append(appid)
    except IOError as e:
        raise(str(e))
        logging.error('-- Problem getting app IDs from file: '+filename)


#write list of app ID's to specified log file
def writeAppIDs(idlist):
    try:
        with open(appidfile,'a+') as logfile:
            for appid in idlist:
                logfile.write(appid+"\n")
        logging.info('-- Wrote all extracted app IDs to file')
    except IOError as e:
        raise('-- Write Log: '+logfname+' I/O error({0}): {1}'.format(e.errno,e.strerror))
        logging.error('-- Problem writing app IDs to log')

if __name__ == '__main__':
    scriptpath = os.path.dirname(os.path.abspath(__file__))
    filesdir = os.path.join(scriptpath, 'files', 'PAIR', 'pairbulk-full-')
    appidfile = os.path.join(scriptpath, 'files', 'PAIR', 'pair_app_ids.txt')
    publicappids = []

    #logging configuration
    logging.basicConfig(
                        filename='logs/extractpairappids-log-'+time.strftime('%Y%m%d')+'.txt',
                        level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s -%(message)s',
                        datefmt='%Y%m%d %H:%M:%S'
                       )
    parser = argparse.ArgumentParser()
    parser.add_argument(
                        '-f',
                        '--filedate',
                        required=True,
                        help='Specify filedate in filename - format: YYYYMMDD',
                        type=str
                       )
    args = parser.parse_args()
    logging.info("-- SCRIPT ARGUMENTS ------------")
    logging.info("-- File Date set to: "+str(args.filedate))
    logging.info("-- [JOB START]  ----------------")

    filesdir = os.path.join(filesdir+args.filedate+'-json')
    logging.info('-- Processing files in folder: '+filesdir)
    if os.path.isdir(os.path.join(scriptpath, filesdir)):
        for filename in glob.glob(os.path.join(scriptpath, filesdir,'*.json')):
            extractIDs(filename)

        #sort app id's in order
        publicappids.sort()
        logging.info('-- Total number of app IDs extracted: '+str(len(publicappids)))
        logging.info('-- Writing all extracted public app IDs to file')
        writeAppIDs(publicappids)
    else:
        logging.error('-- PAIR App ID file path does not exist')

    logging.info("-- [JOB END] -------------------")
