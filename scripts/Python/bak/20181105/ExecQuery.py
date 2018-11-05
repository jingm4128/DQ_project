# -*- coding: utf-8 -*-
"""
Created on Sun Apr  1 15:46:11 2018

@author: IBM
"""

import MySQLdb #mysqlclient
import pandas as pd
from datetime import datetime

from config import ExecQuery_config
host = ExecQuery_config['mysql_conninfo']['host']
user = ExecQuery_config['mysql_conninfo']['user']
passwd = ExecQuery_config['mysql_conninfo']['passwd']
temp_data_dir = ExecQuery_config['temp_data_dir']


def main():
    result = ExecQuery('us','select * from us.equity_daily limit 10;', True)
    print(result)
    
    query = """LOAD DATA INFILE 'E:\\\\Work\\\\PartTime\\\\DQ_project\\\\data\\\\QuandlWiki\\\\partial\\\\raw\\\\WIKI_20180327.partial2.csv' 
    INTO TABLE us.equity_daily 
    COLUMNS TERMINATED BY ','
    OPTIONALLY ENCLOSED BY '"'
    ESCAPED BY '"'
    LINES TERMINATED BY '\\n';"""
    print(query)
    #ExecQuery('us',query, True)
    
    query = "select * from us.px_dist where ticker = 'JNJ' and model = 'crude';"
    data = ExecQuery('us', query, True, True)
    print(data)



#########################################
### The Function
#########################################
def ExecQuery(database, query, fetch_data = False, to_dataframe = False):
    conn = MySQLdb.connect(host=host,user=user,passwd=passwd,db=database, connect_timeout=6000)
    cursor = conn.cursor()
    cursor.execute(query)
    if fetch_data:
        data = cursor.fetchall()
        data = [list(i) for i in data]
        if to_dataframe:
            data = pd.DataFrame(data, columns=[i[0] for i in cursor.description])
    else:
        data = None
    conn.close()
    return data

def LoadDataFrame2DB(db, dataframe, table_name):
    temp_file = temp_data_dir + '.'.join(['temp_load',table_name,(datetime.now()).strftime('%Y%m%d.%H%M%S'),'csv'])
    dataframe.to_csv(temp_file, index=False)
    load_query = """
                 LOAD DATA INFILE '""" + temp_file + """' 
                 INTO TABLE """ + table_name + """  
                 COLUMNS TERMINATED BY ','
                 OPTIONALLY ENCLOSED BY '"'
                 ESCAPED BY '"'
                 LINES TERMINATED BY '\\r\\n'
                 IGNORE 1 ROWS
                 ;commit;
                 """
    print(load_query)
    ExecQuery(db, load_query)


######################################
### Execute if main
######################################
if __name__ == '__main__':
    main()