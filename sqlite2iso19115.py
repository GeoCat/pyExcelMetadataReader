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
from collections import OrderedDict
# Dictionary with generic provider info 
global_provider_info = {
    "organization": "schieland en de Krimpenerwaard",
    "email": "info@hhsk.nl",
    "telefon": "010 45 37 200",
    "fax" : "010 45 37 200",    
}


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
        """Gets a specific table
        
        :returns: list || None
        
        """
        try:
            result = self.cursor.execute("select * from {};".format(table))
        except:
            print("table not found")
            return None
        
        return result.fetchall()
    
    def get_fc_data(self,code):
        """Gets the row from the table factsheewt
        
        :returns: list || None
        """
        try:
            result = self.cursor.execute("select * from factsheet where code=?",(code,))    
        except Exception as e:
            print(e)
            return None
        
        return result.fetchall()
    
    def get_attr_data(self,code):
        """Gets the row from the table attr and make an attribute dictionary with list of attributes
        
        :returns: list || None
        """
        try:
            result = self.cursor.execute("select attr,desc,unit from attr where code=?",(code,))
        
        except Exception as e:
            print(e)
            return None
        
        return result.fetchall()
    
            
        
        
        #column_list = (Eenh1,Attribuut1,Omschrijving1)
         
        #column_list = [("Attribuut"+str(n),"Omschrijving"+str(n),"Eenh"+str(n)) for n in range(1,21)] #[('Attribuut1', 'Omschrijving1', 'Eenh1'), ('Attribuut2', 'Omschrijving2', 'Eenh2'), ('Attribuut3', 'Omschrijving3', 'Eenh3'), ('Attribuut4', 'Omschrijving4', 'Eenh4'), ('Attribuut5', 'Omschrijving5', 'Eenh5'), 
        #column_string = []
        #[[column_string.append(x) for x in y] for y in column_list]
        #column_string = ",".join(column_string)
        #sql = "select {} from factsheet where code=?".format(column_string)
        #result = self.cursor.execute(sql,(code,))
        #result = result.fetchall()
        #Assuming only one result:
        #try:
        #    result = result[0]
        #    result = dict(result)
        #except Exception as e:
        #    print(e)
        #    return None
        #tmp=[]
        #deserialize into a dictorary
        #for attr_tuple in column_list:
        #    tmp.append({
        #        attr_tuple[0]:result[attr_tuple[0]],
        #        attr_tuple[1]:result[attr_tuple[1]]        
                        
        #                })
             
        #print(tmp)
        #print(set(result))
        
        #try:
        #    result = self.cursor.execute("select  from attr where code=?",(code,))    
        #except Exception as e:
        #    print(e)
        #    return None
        
        #return result.fetchall()
        
        
#./data/Schieland.sqlite

def get_filename(row):
    """Makes a filename based on code content in row, otherwise returns a uuid
    
    :returns: string
    """
    if row.get("Code",None) is None:
        return uuid.uuid4()+".xml"
    else:
        return row["Code"]+".xml"
        


@click.command()
@click.option('--sqlitedb',nargs=1,default = "./data/Schieland.sqlite", type=click.Path(exists=True),required=True,help='SQlite file location')
@click.option('--outputdir',nargs=1,default = "./output",type=click.Path(exists=True),required=True,help='Output dir')
@click.option('--template-metadata',default = "./templates/iso19115_schieland.xml.template" ,nargs=1,type=click.Path(exists=True),help="iso 19115 Template to use")
@click.option('--template-fc',default = "./templates/iso19110_schieland.xml.template" ,nargs=1,type=click.Path(exists=True),help="iso 19115 Template to use")
def main(sqlitedb,outputdir,template_metadata,template_fc):
    """Main function that calls all the code """

    sqlite_connector = SQliteConnector(sqlitedb)
    table_gegevens = sqlite_connector.get_table("Gegevens")
    

    for row_metadata in table_gegevens:
        row_metadata = dict(row_metadata)
        
        file_name = get_filename(row_metadata)
        # if code is none then set a uuuid and use it as file identifer
        
        if row_metadata.get("Code",None):
            print(row_metadata["Code"])
            row_fc = sqlite_connector.get_fc_data(row_metadata["Code"]) 
            row_fc_attr = sqlite_connector.get_attr_data(row_metadata["Code"]) #{'code': 'WS01_F', 'attr': 'Code', 'unit': 'OWA-XXX', 'desc': 'Unieke code'}
            fc_attr = []
            
            
            #Assuming that row_fc
            if row_fc:
                row_fc = dict(row_fc[0])
            if  row_fc_attr:
                row_fc["ATTRLIST"] = [dict(item) for item in row_fc_attr]
           #     row_fc["ATTRLIST"] =  
           # print(row_fc["ATTRLIST"])    
                
            #print(dict(row_fc[0])) 
            
        else:
            row_metadata["Code"] = uuid.uuid4()
        
        
        file_name_metadata = row_metadata["Code"] + ".xml"
        file_name_feature = row_metadata["Code"] + "_FC.xml"
        
        #YYYY-MM-DD is accepted dateformat in the ISO
        row_metadata["today"] = datetime.date.today().isoformat()
        row_fc["today"] = row_metadata["today"]
        #TODO
        #ATTRLIST
        
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
        
        
        metadata_record = render(template_metadata, {**row_metadata,**global_provider_info} ).encode(encoding='UTF-8')
        with open(os.path.join(outputdir,file_name_metadata),"wb") as f1:
            f1.write(metadata_record)
        
        
        feature_record = render(template_fc,{**row_fc,**global_provider_info}).encode(encoding="UTF-8")
        with open(os.path.join(outputdir,file_name_feature),"wb") as f2:
            f2.write(feature_record)
        
        break
    print("Done")
        
    

if __name__ == '__main__':
    main()