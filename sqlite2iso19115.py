#/usr/bin/env python3
#-*- coding: utf-8 -*-
"""Module for conversion from sqlite structure to iso 19115"""
from uuid import uuid4



__title__      = 'Sqlite3 iso 19115 converter'
__summary__    = """sqlite converter to iso 19115. Data table in 'Factsheet' will be converted to XML stored in an output folder (need to be created first)"""
__author__     = 'Jorge Samuel Mendes de Jesus'
__date__       = '04-April-2018'
__version__    = '1.0'
__email__      = 'jorge.dejesus@geocat.net'


import sqlite3
import click
import sys,os 
import jinja2
import datetime
import uuid

def render(tpl_path, context):
    """Jinja2 render function"""
    path, filename = os.path.split(tpl_path)
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(path or './')
    ).get_template(filename).render(context)




class SQliteConnector():
    
    """SQLITE class that connects to database and and maps SQL to data requirements"""
    
    def __init__(self,db_path):
        """ Class contructor
    
        :param db_path: string path to sqlite
        :returns: SQliteConnector object
    
        """
        
        self.db_path = db_path
        self.cursor = None
        
        self.__load()
        
    
    def __load(self):
        
        """ Connects and return a cursor to sqlite 
        
        :returns: sqlite3.Cursor
        
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA quick_check")
        except sqlite3.DatabaseError:
            print("file is encrypted or is not a database, finishing script")
            sys.exit(1)
        
        conn.row_factory = sqlite3.Row
        self.cursor = conn.cursor()

    def get_table(self,table):
        """Gets a specific table"""
        try:
            result = self.cursor.execute("select * from {};".format(table))
        except:
            print("table not found")
            return None
        
        return result.fetchall()    
            
        
#./data/Schieland.sqlite

def get_filename(row):
    """Makes a filename based on code content in row, otherwise returns a uuid"""
    if row.get("Code",None) is None:
        return uuid.uuid4()+".xml"
    else:
        return row["Code"]+".xml"
        


@click.command()
@click.option('--sqlitedb',nargs=1,default = "./data/Schieland.sqlite", type=click.Path(exists=True),required=True,help='SQlite file location')
@click.option('--outputdir',nargs=1,default = "./output",type=click.Path(exists=True),required=True,help='Output dir')
@click.option('--template',default = "./templates/schieland.xml" ,nargs=1,type=click.Path(exists=True),help="iso 19115 Template to use")
def main(sqlitedb,outputdir,template):
    
    """Main function that calls all the code """

    sqlite_connector = SQliteConnector(sqlitedb)
    table_gegevens = sqlite_connector.get_table("factsheet")
    for row in table_gegevens:
        row = dict(row)
        
        file_name = get_filename(row)
        # if code is none then set a uuuid and use it as file identifer
        if not row.get("Code", None):
            row["Code"] = uuid.uuid4()
        
        
        file_name = row["Code"] + ".xml"
        #YYYY-MM-DD is accepted dateformat in the ISO
        row["today"] = datetime.date.today().isoformat()
        
        #PASOP! EigenaarVakafdeling is in factsheet
        #PASOP! CLASSIFICATIE is missing from all the tables
        #PASOP! LICENTIE is missing
        #PASOP! URI_LICENTIE is missing
        # <!-- utf8 if empty -->{% if KARAKTERSET is defined %}
        # THEMA IS MISSING
        #OMGRENZENDE_DRIEHOEK is missing
        #LOCATIE is missing
        #STARTDATUM_DATASET and EINDDATUM_DATASET is missing
        #FCID to be done
        #<gmd:URL>{{ Database }}</gmd:URL> ??? databaseobject?? HHSK.PZ01_Beheergebieden
        
        
        xml_record = render(template, row).encode(encoding='UTF-8')
        with open(os.path.join(outputdir,file_name),"wb") as f1:
            f1.write(xml_record)
        break
    print("Done")
        
    

if __name__ == '__main__':
    main()