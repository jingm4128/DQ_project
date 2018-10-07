# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

#import numpy as np ## not used in this script for now
import pandas as pd
from datetime import datetime
import os
import glob
from ExecQuery import ExecQuery
#import quandl ## later imported in the function
#import zipfile ## later imported in the function

from config import get_data_config


def main():
    GetData(get_data_config)
    

#########################################
### The Function
#########################################
def GetData(get_data_config):
    # the conf
    data_dir = get_data_config['Quandl_partial_dir']
    api_key = get_data_config['Quandl_api_key']
    col_names = get_data_config['Quandl_col_names']
    db_name = get_data_config['mysql_database']
    table_name = get_data_config['mysql_table_name']
    
    raw_dir = data_dir + 'raw/'
    proc_dir = data_dir + 'proc/'
    
    raw_file_list = DumpBulkDataFromQuandl(raw_dir, api_key)
    print(raw_file_list)
    
    proc_file_dict = ProcessData(proc_dir, raw_file_list, col_names, True)
    print(proc_file_dict)
    
    LoadData(proc_file_dict, db_name, table_name, True)
    
    #historical
    #ProcessData('E:/Work/PartTime/DQ_Project/data/QuandlWiki/hist/proc/',['E:/Work/PartTime/DQ_Project/data/QuandlWiki/hist/raw/WIKI_PRICES.csv'], col_names)
    #LoadData(['E:/Work/PartTime/DQ_Project/data/QuandlWiki/hist/proc/proc_WIKI_PRICES.csv'], db_name, table_name)
    
    
    


#########################################
### Helper Functions
#########################################
    
### 1. DumpBulkDataFromQuandl ###########
def DumpBulkDataFromQuandl(raw_dir, api_key):  
    # defininations
    zip_file_name = raw_dir + datetime.strftime(datetime.now(),'%Y%m%d.%H%M%S') + '.zip'
    
    # bulkdownload
    import quandl
    quandl.ApiConfig.api_key = api_key
    quandl.bulkdownload("WIKI", download_type="partial", filename=zip_file_name)
    
    # remove all the existing csv files
    to_remove_list = glob.glob(raw_dir + '*.csv')
    for f in to_remove_list:
        os.remove(f)
    
    # upzip and rename
    import zipfile
    zip_ref = zipfile.ZipFile(zip_file_name, 'r')
    zip_ref.extractall(raw_dir)
    zip_ref.close()
    
    raw_file_list = glob.glob(raw_dir + '*.csv')
    raw_file_list = [f.replace('\\','/') for f in raw_file_list]
    return raw_file_list


### 2. ProcessData ######################
def ProcessData(proc_dir, raw_file_list, col_names, keep_lastest=False):
    proc_file_dict = {}
    
    for raw_file_name in raw_file_list:
        #raw_file_name = raw_file_list[0] ###DEBUG
        #keep_lastest=True ###DEBUG
        
        # read the data
        data = pd.read_csv(raw_file_name, header=None, names = col_names)
        #data = pd.read_csv(raw_file_name) ###DEBUG, hist
        
        if keep_lastest:
            # only keep the data when date = date in the file name
            datex = ((raw_file_name.split('/')[-1]).split('.')[0]).split('_')[1]
            datex = datetime.strftime(datetime.strptime(datex,'%Y%m%d'), '%Y-%m-%d')
            data = data[data['date']==datex]
        
        # transform the format of the data
        data['date'] = pd.to_datetime(data['date']).dt.strftime('%Y/%m/%d')
                
        # generate the file name based on the raw file name
        proc_file_name = proc_dir + 'proc_' + raw_file_name.split('/')[-1]
        
        # output with nan being 'NULL'
        data.to_csv(proc_file_name, na_rep='NULL', index=False, header=None)
        
        
        proc_file_dict.update({proc_file_name:datex})
    
    return proc_file_dict


### 3. LoadData #########################
def LoadData(proc_file_dict, db_name, table_name, delete=False):
    for f in proc_file_dict.keys():
        if delete:
            del_query = "delete from " + table_name + " where date = '" + proc_file_dict[f] + "'; commit;"
            print(del_query)
            ExecQuery(db_name, del_query)
        
        load_query = """
                     LOAD DATA INFILE '""" + f.replace('/','\\\\') + """' 
                     INTO TABLE """ + table_name + """  
                     COLUMNS TERMINATED BY ','
                     OPTIONALLY ENCLOSED BY '"'
                     ESCAPED BY '"'
                     LINES TERMINATED BY '\\r\\n'
                     #IGNORE 1 ROWS
                     ;commit;
                     """
        print(load_query)
        ExecQuery(db_name, load_query)


#########################################
### Execute if main
#########################################
if __name__ == '__main__':
    main()



#########################################
### Examples/Explanations
#########################################
    
def DumpDfDataFromQuandl(sd, ed, ticker):  
    # bulkdownload
    import quandl
    quandl.ApiConfig.api_key = get_data_config['Quandl_api_key']
    df = quandl.get_table('WIKI/PRICES'
                          , qopts = {'columns': ['ticker', 'date', 'adj_close']}
                          , date={'gte': sd, 'lte': ed}
                          , ticker=ticker
                          , paginate=True)
    return df

def DumpDataFromQuandlExamples():
    import quandl
    
    ### Here are a few ways to dump the data from Quandl, to data frame
    # 0. load the api_key
    quandl.ApiConfig.api_key = get_data_config['Quandl_api_key']
    
    # 1. get_table method: can get one day or multiple days of data
    print(quandl.get_table('WIKI/PRICES', date='2018-03-28', ticker='AAPL'))

    print(quandl.get_table('WIKI/PRICES', ticker = ['AAPL', 'MSFT', 'WMT'], 
                        #qopts = { 'columns': ['ticker', 'date', 'adj_close'] }, 
                        date = { 'gte': '2016-12-15', 'lte': '2016-12-31' }, 
                        paginate=True))
    
    # 2. get method: mostly for a time series
    print(quandl.get("WIKI/AAPL", trim_start = "2012-12-21", trim_end = "2013-01-01"))
    
    # 3. bulkdownload method: download all the sybmbols as of the last available date
    print(quandl.bulkdownload("WIKI", download_type="partial", filename="E:/Work/PartTime/DQ_Project/temp/WIKI.zip"))