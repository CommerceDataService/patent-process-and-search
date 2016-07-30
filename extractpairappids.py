#!/usr/bin/env python 3.5

#Author:        Sasan Bahadaran
#Date:          7/30/16
#Organization:  Commerce Data Service
#Description:   This script crawls the directory of public pair files, extracts all
#application ID's from each file, stores it in a list, sorts it, and then writes it
#to a file for further use

import json, glob, os, collections

def extractIDs(fname):
    try:
        fpath,filename = os.path.split(fname)
        with open(fname, 'r') as fd:
            data = json.load(fd)
            apps = data['PatentBulkData']
            for app in apps:
                appid = app['applicationDataOrProsecutionHistoryDataOrPatentTermData'][0]['applicationNumberText']['value']
                publicappids.append(appid)
    except IOError as e:
        raise(e)

#write list of app ID's to specified log file
def writeAppIDs(idlist):
    try:
        with open(appidfile,'a+') as logfile:
            for appid in idlist:
                logfile.write(appid+"\n")
    except IOError as e:
        raise('-- Write Log: '+logfname+' I/O error({0}): {1}'.format(e.errno,e.strerror))

if __name__ == '__main__':
    scriptpath = os.path.dirname(os.path.abspath(__file__))
    filesdir = os.path.join(scriptpath, 'files', 'PAIR', 'pairbulk-full-20160729-json')
    appidfile = os.path.join(scriptpath, 'files', 'PAIR', 'pair_app_ids.txt')
    publicappids = []

    for filename in glob.glob(os.path.join(filesdir,'*.json')):
        extractIDs(filename)

    #sort app id's in order
    publicappids.sort()
    writeAppIDs(publicappids)
