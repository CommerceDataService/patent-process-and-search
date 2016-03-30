#Author:        Sasan Bahadaran
#Date:          2/29/16
#Organization:  Commerce Data Service

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

#crawl through each xml file, find corresponding text doc and add to xml node
for root, dirs, files in os.walk('files/'):
    for name.endswith('.xml') in files:
        if name.endswith('.xml'):
            with open(os.path.join(root,name)) as fd:
                doc = xmltodict.parse(fd.read())
                for x in doc['main']['DATA_RECORD']:
                    value = None
                    pathfolder = getFolder(root,2)
                    if pathfolder.startswith('PTAB'):
                        value = getData(x,'DOCUMENT_IMAGE_ID')
                    elif pathfolder.startswith('PRPS'):
                        value = getData(x,'DOCUMENT_NM')
                    with open(os.path.join(root+'/PDF_image',value+'.txt')) as dr:
                        text = dr.read()
                        setData(x,'DOCUMENT_TEXT',text)
                #transform output to json and save to file with same name
                with open(os.path.join(root,os.path.splitext(name)[0])+'.json','w') as outfile:
                    json.dump(doc,outfile)
