#!/usr/bin/env python

#Author:        Sasan Bahadaran
#Date:          2/29/16
#Organization:  Commerce Data Service
#Description:   This script crawls the files directory and finds the metadata
#xml file that for each set of pdf files.  It then gets the document id from
#the metadata and finds the associated extracted pdf text and adds it to the
#structure of the document, then transforms the document to json and saves it
#to a file.

import json, xmltodict, os

#get value for specified tag from a list
def getData(list,tag):
    value = list[tag]

    return value

#add data with specified tag to existing list
def setData(list,tag,text):
    list[tag] = text

#get specified folder from folder path
def getFolder(root,level):
    folder = root.split(os.path.sep)[level]

    return folder

if __name__ == '__main__':
    #crawl through each main direcotyr and find the metadata xml file
    for root, dirs, files in os.walk('files/'):
        for name in files:
            if name.endswith('.xml'):
                with open(os.path.join(root,name)) as fd:
                    doc = xmltodict.parse(fd.read())
                    #get document id from metadata xml file
                    for x in doc['main']['DATA_RECORD']:
                        value = None
                        pathfolder = getFolder(root,1)
                        if pathfolder.startswith('PTAB'):
                            value = getData(x,'DOCUMENT_IMAGE_ID')
                        elif pathfolder.startswith('PRPS'):
                            value = getData(x,'DOCUMENT_NM')
                        #add extracted pdf text to node
                        with open(os.path.join(root+'/PDF_image',value+'.txt')) as dr:
                            text = dr.read()
                            setData(x,'DOCUMENT_TEXT',text)
                    #transform output to json and save to file with same name
                    with open(os.path.join(root,os.path.splitext(name)[0])+'.json','w') as outfile:
                        json.dump(doc,outfile)
