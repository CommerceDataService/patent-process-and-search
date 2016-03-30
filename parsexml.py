#Author:        Sasan Bahadaran
#Date:          2/29/16
#Organization:  Commerce Data Service

import json, xmltodict, os

#def alterMetadata(x,image_id):



#crawl through each xml file, find corresponding text doc and add to xml node
for root, dirs, files in os.walk('files/'):
    for name in files:
        if name.endswith('.xml'):
            with open(os.path.join(root,name)) as fd:
                doc = xmltodict.parse(fd.read())
                for x in doc['main']['DATA_RECORD']:
                    image_id = None
                    if root.split(os.path.sep)[2].startswith('PTAB'):
                        image_id = x['DOCUMENT_IMAGE_ID']
                    elif root.split(os.path.sep)[2].startswith('PRPS'):
                        image_id = x['DOCUMENT_NM']
                    with open(os.path.join(root+'/PDF_image',image_id+'.txt')) as dr:
                        print (os.path.join(root+'/PDF_image',image_id+'.txt'))
                        text = dr.read()
                        x['DOCUMENT_TEXT'] = text
               
                #transform output to json and save to file with same name
                with open(os.path.join(root,os.path.splitext(name)[0])+'.json','w') as outfile:
                    json.dump(doc,outfile)
