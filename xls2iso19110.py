#/usr/bin/env python3
#-*- coding: utf-8 -*-
"""Module for conversion from excel sheet o iso 19110. This script doesnt have schema validation"""

__title__      = 'Excel to iso 19110 converter'
__summary__    = 'Excel sheet converter to iso 19110.  Gegevensattribuut Gegevensbron Gegevensdomein sheets are used to assemble the XML. The XML will be output to an ouput folder'
__author__     = 'Jorge Samuel Mendes de Jesus'
__date__       = '18-JAN-2018'
__version__    = '1.0'
__email__       = 'jorge.dejesus@geocat.net'

##########  PARAMETERS ######################################
inputXLS = "POC testdata Metadatregister Rittenstaat.xlsx"
TEMPLATE_FILE = "iso19110.xml.template"

#List of string and/or numbers that need to be None
listNone = ["n.v.t","n.v.t.",0]
mandatoryFields = ["GEGEVENSBRON_ID", "GEGEVENSDOMEIN_ID","GEGEVENSVERZAMELING_ID"] 
####################################################

import pandas as pd
import jinja2
import os
from lxml import etree
from collections import OrderedDict
from config import uri_prefix


def render(tpl_path, context):
    """Jinja2 render function"""
    path, filename = os.path.split(tpl_path)
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(path or './')
    ).get_template(filename).render(context)

def delValueNone(dict):
    """Removes keys that has None"""
    d={}
    for k, v in dict.items():
        if v is not None:
            d[k]=v
    return d

def fixDate(dict):
    """The pandas lib datatime makes a YYYY-MM-DD 00:00 representation, 
    but only YYYY-MM-DD is accepted in the ISO. It can also accour as datetime.date"""
    for k,v in dict.items():
        if isinstance(dict[k],pd._libs.tslib.Timestamp):
            dict[k]=v.date()
    return dict


def main(args):

    INPUT_XLS = args.inputexcel.name 
    args.inputexcel.close() #better not to use the open string
    
    OUTPUT_FOLDER = args.outdir
    xls = pd.ExcelFile(INPUT_XLS)

# Now you can list all sheets in the file
print("Avalilables sheets: {}".format(str(xls.sheet_names)))

#lets replace NaN with a easy to process string
dataFrameAttributes = pd.read_excel(xls, 'Gegevensattribuut').fillna(value=listNone[0])
dataFrameDataSource = pd.read_excel(xls, 'Gegevensbron').fillna(value=listNone[0])
dataFrameDataDomain = pd.read_excel(xls, 'Gegevensdomein').fillna(value=listNone[0])


#replace items from NoneList 
[dataFrameAttributes.replace([itemNone], [None],inplace=True) for itemNone in listNone]
[dataFrameDataSource.replace([itemNone], [None],inplace=True) for itemNone in listNone]
[dataFrameDataDomain.replace([itemNone], [None],inplace=True) for itemNone in listNone]


for name, group in dataFrameAttributes.groupby('GEGEVENSVERZAMELING_ID'):
    recordDic={}
    recordDic["URI"] = os.path.join(uri_prefix,name) #<!-- for uri use {{ prefix }}{{ GEGEVENSVERZAMELING_ID }}, prefix is in a config file --> 

    print("Generating XML: for attribute {}".format(name))
    sourceDataID = group["GEGEVENSBRON_ID"].iat[0]
    dataDomainID = group["GEGEVENSDOMEIN_ID"].iat[0]
    dataCollectionID = group["GEGEVENSVERZAMELING_ID"].iat[0]
    
    fileName="FC:{}:{}:{}.xml".format(sourceDataID,dataDomainID,dataCollectionID)
    
    recordDic["GEGEVENSBRON_ID"] = sourceDataID
    recordDic["GEGEVENSDOMEIN_ID"] = dataDomainID
    recordDic["GEGEVENSVERZAMELING_ID"] = dataCollectionID
    recordDic["UUID"]=fileName[:-3]
    
    dataDomainRow = dataFrameDataDomain[dataFrameDataDomain["GEGEVENSDOMEIN_ID"].str.match(dataDomainID)]
    
    #easier to inject all dictionary and let the template to decide instead of cheerypickin
    recordDic.update(dataDomainRow.to_dict(orient="records")[0])

       
    sourceDataDic=dataFrameDataSource[dataFrameDataSource['GEGEVENSBRON_ID'].str.match(sourceDataID)].to_dict(orient="records")[0]
    recordDic.update(sourceDataDic)
    attributeDataFrame=group.drop(["GEGEVENSBRON_ID","GEGEVENSDOMEIN_ID","GEGEVENSVERZAMELING_ID"],1)
    
    attributeList=[]
    for record in attributeDataFrame.iterrows():
        record = record[1].to_dict()
        record = {k:v for k, v in record.items() if v is not None}
        record["URI"] = os.path.join(recordDic["URI"],record["NAAM"])
        attributeList.append(record)
        
    recordDic["ATTRLIST"]=attributeList    
  
    if recordDic.get("BEREIK",None):
            record["BEREIK"]=record["BEREIK"].split("/")

    recordDic = fixDate(recordDic)
    xmlRecord = render(TEMPLATE_FILE, recordDic).encode(encoding='UTF-8')
    
    with open(os.path.join(OUTPUT_FOLDER,fileName),"wb") as f1:
        f1.write(xmlRecord)
    
if __name__ == "__main__":
    
    
    parser = argparse.ArgumentParser(description = __summary__)    
    #File location
    parser.add_argument('--excelsheet',dest="inputexcel", type=argparse.FileType('r', encoding='UTF-8'), 
                        required=False,  default="POC testdata Metadatregister Rittenstaat.xlsx", help="Excel file/path with data")
    
    #Directory 
    parser.add_argument('--outdir',dest="outdir", required=False,  default="./output", 
                        help="Directory path that will contain the XML", type=is_dir)
    
    
    main(args=parser.parse_args())
    