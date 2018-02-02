#/usr/bin/env python3
#-*- coding: utf-8 -*-
"""Module for conversion from excel sheet o iso 19115"""


__title__      = 'Excel to iso 19115 converter'
__summary__    = """Excel sheet converter to iso 19115. Data table in 'Gegevensverzameling' will be converted to XML stored in an output folder (need to be created first)"""
__author__     = 'Jorge Samuel Mendes de Jesus'
__date__       = '18-JAN-2018'
__version__    = '1.0'
__email__      = 'jorge.dejesus@geocat.net'

########## INTERNAL CONTANT  PARAMETERS ##########################
TEMPLATE_FILE = "iso19115.xml.template"
SCHEMA_LOCATION = "http://schemas.opengis.net/iso/19139/20060504/gmd/gmd.xsd"
#List of string and/or numbers that need to be None
listNone = ["n.v.t","n.v.t.",0]
####################################################

import pandas as pd
import jinja2
import os
from lxml import etree
import argparse


 
def render(tpl_path, context):
    path, filename = os.path.split(tpl_path)
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(path or './')
    ).get_template(filename).render(context)




def fixDate(dict):
    """The pandas lib datatime makes a YYYY-MM-DD 00:00 representation, 
    but only YYYY-MM-DD is accepted in the ISO"""
    for k,v in dict.items():
        if isinstance(dict[k],pd._libs.tslib.Timestamp):
                    dict[k]=v.date()
    return dict


def is_dir(dirname):
    """Checks if a path is an actual directory"""
    if not os.path.isdir(dirname):
        msg = "{0} is not a directory".format(dirname)
        raise argparse.ArgumentTypeError(msg)
    else:
        return dirname

    
def main(args):
    
    INPUT_XLS = args.inputexcel.name 
    args.inputexcel.close() #better not to use the open string
    
    SCHEMA_VALIDATION = args.schema
    OUTPUT_FOLDER = args.outdir

    xls = pd.ExcelFile(INPUT_XLS)
    
    #lets replace NaN with a easy to process string
    dataFrame = pd.read_excel(xls, 'Gegevensverzameling').fillna(value=listNone[0])
    print("Processing sheet: {}".format("Gegevensverzameling"))
    
    
    #replace items from NoneList 
    [dataFrame.replace([itemNone], [None],inplace=True) for itemNone in listNone]
    
    
    for record in dataFrame.iterrows():
        record = record[1].to_dict()
        #Filter remover any None values
        record = {k:v for k, v in record.items() if v is not None}
        
        if record.get("TREFWOORD",None):
            record["TREFWOORD"]=record["TREFWOORD"].split("#")
        
        
        fixDate(record)
        fileName = "NL:PRVGRN:{0}:{1}:{2}.xml".format(record.get("GEGEVENSBRON_ID",None),
                                              record.get("GEGEVENSDOMEIN_ID",None),
                                              record.get("GEGEVENSVERZAMELING_ID",None))
        print("Processing file:{}".format(fileName))
        
        xmlRecord = render(TEMPLATE_FILE, record).encode(encoding='UTF-8')
        xmlDoc = etree.fromstring(xmlRecord)
        
        if SCHEMA_VALIDATION: 
            xmlSchema = etree.XMLSchema(etree.parse(SCHEMA_LOCATION))
            xmlSchema.assertValid(xmlDoc)
            print("Schema Validation of {}: OK".format(fileName))
        
        fPath = os.path.join(OUTPUT_FOLDER,fileName)
        fOut = open(fPath,'wb')
        xmlDoc.getroottree().write(fOut,pretty_print=True)
    
        
    
    print(" All Done")

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description = __summary__)
    schema_parser = parser.add_mutually_exclusive_group(required=False)
    #Schema descriptom
    schema_parser.add_argument('--schema', dest='schema', action='store_true',help="Use gmd.xsd  schema for validation. This maybe time consuming" )
    schema_parser.add_argument('--no-schema', dest='schema', action='store_false', help="Dont use schema validation - this is the default and fastest option")
    parser.set_defaults(schema=False)
    
    #File location
    parser.add_argument('--excelsheet',dest="inputexcel", type=argparse.FileType('r', encoding='UTF-8'), 
                        required=False,  default="POC testdata Metadatregister Rittenstaat.xlsx", help="Excel file/path with data")
    
    #Directory 
    parser.add_argument('--outdir',dest="outdir", required=False,  default="./output", 
                        help="Directory path that will contain the XML", type=is_dir)
    
    
    main(args=parser.parse_args())
    