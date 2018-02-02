#/usr/bin/env python3
#-*- coding: utf-8 -*-
from dicom.util.dump import pretty_print

#TICKET: https://eos.geocat.net/redmine/issues/11874
__doc__        = ''
__title__      = ''
__summary__    = ''
__author__     = 'Jorge Samuel Mendes de Jesus'
__date__       = '18-JAN-2018'
__version__    = '1.0'
__email__       = 'jorge.dejesus@geocat.net'

##########  PARAMETERS ######################################
inputXLS = "POC testdata Metadatregister Rittenstaat.xlsx"
#/home/jesus/git/metadata/iso19110.xml.template
TEMPLATE_FILE = "iso19110.xml.template"
SCHEMA_LOCATION = "http://schemas.opengis.net/iso/19139/20060504/gmd/gmd.xsd"
SCHEMA_VALIDATION = False
OUTPUT_FOLDER = "./output"
#List of string and/or numbers that need to be None
listNone = ["n.v.t","n.v.t.",0]
mandatoryFields = ["GEGEVENSBRON_ID", "GEGEVENSDOMEIN_ID","GEGEVENSVERZAMELING_ID"] 
####################################################

import pandas as pd
import jinja2
import os
from lxml import etree


 
def render(tpl_path, context):
    path, filename = os.path.split(tpl_path)
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(path or './')
    ).get_template(filename).render(context)

def delValueNone(dict):
    d={}
    for k, v in dict.items():
        if v is not None:
            d[k]=v
    return d
def fixDate(dict):
    """The pandas lib datatime makes a YYYY-MM-DD 00:00 representation, 
    but only YYYY-MM-DD is accepted in the ISO"""
    for k,v in dict.items():
        if isinstance(dict[k],pd._libs.tslib.Timestamp):
                    dict[k]=v.date()
    return dict



xls = pd.ExcelFile(inputXLS)
# Now you can list all sheets in the file
print("Avalilables sheets: {}".format(str(xls.sheet_names)))

#lets replace NaN with a easy to process string
dataFrame = pd.read_excel(xls, 'Gegevensverzameling').fillna(value=listNone[0])
print("Processing sheet: {}".format("Gegevensverzameling"))


#replace items from NoneList 
[dataFrame.replace([itemNone], [None],inplace=True) for itemNone in listNone]


for record in dataFrame.iterrows():
    record = record[1].to_dict()
    #Filter remover any None values
    record = {k:v for k, v in record.items() if v is not None}
    fixDate(record)
    fileName = "NL:PRVGRN:{0}:{1}:{2}.xml".format(record.get("GEGEVENSBRON_ID",None),
                                          record.get("GEGEVENSDOMEIN_ID",None),
                                          record.get("GEGEVENSVERZAMELING_ID",None))
    print("Processing file:{}".format(fileName))
    
    xmlRecord = render('iso19115.xml.template', record).encode(encoding='UTF-8')
    xmlDoc=etree.fromstring(xmlRecord)
    
    if SCHEMA_VALIDATION: 
        xmlSchema = etree.XMLSchema(etree.parse(SCHEMA_LOCATION))
        xmlSchema.assertValid(xmlDoc)
    
    fPath = os.path.join(OUTPUT_FOLDER,fileName)
    fOut = open(fPath,'wb')
    xmlDoc.getroottree().write(fOut,pretty_print=True)

    

print("Done")