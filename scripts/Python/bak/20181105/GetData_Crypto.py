# -*- coding: utf-8 -*-
"""
Created on Mon Apr  1 10:46:11 2018

@author: Jing Ma
"""

#import numpy as np ## not used in this script for now
import pandas as pd
from datetime import datetime
import os
import glob
from ExecQuery import ExecQuery
import time
#import quandl ## later imported in the function
#import zipfile ## later imported in the function

from config import GetData_config


def main():
    GetData(GetData_config)
    

#########################################
### The Function
#########################################
def GetData(GetData_config):
    # the conf
    data_dir = GetData_config['AlphaVantage']['dir']['crypto']
    api_key = GetData_config['AlphaVantage']['api_key']
    api_query_timegap_sec = GetData_config['AlphaVantage']['query_timegap_sec']
    raw_data_columns = GetData_config['AlphaVantage']['raw_data_columns']['crypto']
    db_columns = GetData_config['Database']['crypto']['db_columns']
    database = GetData_config['Database']['crypto']['database']
    px_table_name = GetData_config['Database']['crypto']['mysql_recent_px_table_name']
    pairs_dict = GetData_config['Database']['crypto']['pairs_dict']
    
    raw_dir = data_dir + 'raw/'
    proc_dir = data_dir + 'proc/'
    
    #datex_dict = GetDatexDict(datetime.now())
    # create different format for the start and enc date to load
    datex_dict = GetDatexDict(datetime.strptime('20181024','%Y%m%d')
                            , datetime.strptime('20181031','%Y%m%d'))
    
    
    # Download the price/volume data from AlphaVantage
    print('dumping prices data...')
    raw_file_list = DumpDailyDataFromAlphav(raw_dir, api_key, api_query_timegap_sec, pairs_dict, datex_dict, False)
    #print(raw_file_list)
    
    # Process the data downloaded
    print('processing prices data...')
    #raw_file_list = [raw_dir + '.'.join([t,'20140101','20181024','csv']) for t in pairs_dict.keys()]
    proc_file_list = ProcessDailyAlphavData(proc_dir, raw_file_list, raw_data_columns, db_columns, datex_dict, True)
    #print(proc_file_list)
    
    # Load the data to the database
    print('loading prices data...')
    #proc_file_list = [proc_dir + 'proc.20140101.20181024.csv']
    LoadData(proc_file_list, database, px_table_name, datex_dict, True)
    


#########################################
### Functions
#########################################

### 1. Dump Data ###########
def DumpDailyDataFromAlphav(raw_dir, api_key, api_query_timegap_sec, pairs_dict, datex_dict, clear_dir=False):
    import urllib
    
    data_set = 'DIGITAL_CURRENCY_DAILY'
    #outputsize = 'full'
    #outputsize = 'compact'
    #url_base = 'https://www.alphavantage.co/query?' +'outputsize='+outputsize+'&'
    url_base = 'https://www.alphavantage.co/query?'
    start_datex = datex_dict['start']['datex']
    end_datex = datex_dict['end']['datex']
    raw_file_list = []
    
    # clear the dir
    if clear_dir:
        for f in glob.glob(raw_dir + '*.csv'): os.remove(f)
    
    i=1
    # dump data
    for p in pairs_dict.keys():
        print(p)
        print(i)
        i+=1
        raw_file_name = raw_dir + '.'.join([p,start_datex,end_datex,'csv'])
        data_file_url = url_base+'function='+data_set+'&symbol='+pairs_dict[p]['symbol']+'&market='+pairs_dict[p]['market']+'&apikey='+api_key+'&datatype=csv'
        print(data_file_url)
        try:
            urllib.request.urlretrieve (data_file_url, raw_file_name)
            raw_file_list.append(raw_file_name)
        except urllib.request.HTTPError:
            #AXON
            print('pair '+ p + ' not availabe, skip!')
            continue
        time.sleep(api_query_timegap_sec)
    
    return raw_file_list



### 2. ProcessData ######################
def ProcessDailyAlphavData(proc_dir, raw_file_list, raw_data_columns, db_columns, datex_dict, keep_lastest=False):
    proc_file_list = []
    start_datex = datex_dict['start']['datex']
    end_datex = datex_dict['end']['datex']
    data_df_list = []
    i=1
    
    for raw_file_name in raw_file_list:
        #raw_file_name = raw_file_list[1] ###DEBUG
        #keep_lastest=True ###DEBUG
        ticker = (raw_file_name.split('/')[-1]).split('.')[0]
        print(ticker)
        print(i)
        i+=1
        # read the data
        try:
            data = pd.read_csv(raw_file_name, header=0, names = raw_data_columns, index_col=False) 
        except pd.errors.ParserError:
            print('ERROR: Could not parse the data in: ' + raw_file_name)
            continue
        
        if keep_lastest:
            # only keep the data when date = date in the file name
            data = data[data['date'] >= datex_dict['start']['datex_dash']]
            data = data[data['date'] <= datex_dict['end']['datex_dash']]
        
        # transform the format of the data
        data['date'] = pd.to_datetime(data['date']).dt.strftime('%Y/%m/%d')
        data['ticker'] = ticker
        data_df_list.append(data[ db_columns ])
    
    agg_data = pd.concat(data_df_list, ignore_index=True)
    # generate the file name based on the raw file name
    proc_file_name = proc_dir + '.'.join(['proc',start_datex,end_datex,'csv'])
    
    # output with nan being 'NULL'
    agg_data.to_csv(proc_file_name, na_rep='NULL', index=False, header=None)       
    
    # update the dict
    proc_file_list.append(proc_file_name)
    return proc_file_list



### 3. LoadData #########################
def LoadData(proc_file_list, database, table_name, datex_dict, delete=False):
    for f in proc_file_list:
        if delete:
            del_query = """delete from """ + table_name + """ 
                           where date >= '""" + datex_dict['start']['datex'] + """'
                           and date <= '""" + datex_dict['end']['datex'] + """'
                           ; commit;
                        """
            print(del_query)
            ExecQuery(database, del_query)
        
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
        ExecQuery(database, load_query)





#########################################
### Helper Functions
#########################################
def GetDatexDict(start_date, end_date):
    curr_datex = datetime.strftime(datetime.now(),'%Y%m%d')
    curr_datex_dash = '-'.join([curr_datex[:4],curr_datex[4:6],curr_datex[6:8]])
    curr_datex_slash = '/'.join([curr_datex[:4],curr_datex[4:6],curr_datex[6:8]])
    
    start_datex = datetime.strftime(start_date,'%Y%m%d')
    start_datex_dash = '-'.join([start_datex[:4],start_datex[4:6],start_datex[6:8]])
    start_datex_slash = '/'.join([start_datex[:4],start_datex[4:6],start_datex[6:8]])
    
    end_datex = datetime.strftime(end_date,'%Y%m%d')
    end_datex_dash = '-'.join([end_datex[:4],end_datex[4:6],end_datex[6:8]])
    end_datex_slash = '/'.join([end_datex[:4],end_datex[4:6],end_datex[6:8]])
    
    #datex_dash = datetime.strftime(datetime.strptime(datex,'%Y%m%d'), '%Y-%m-%d')
    #datex_slash = datetime.strftime(datetime.strptime(datex,'%Y%m%d'), '%Y/%m/%d')
    datex_dict = {'start':{'datex':start_datex
                           ,'datex_dash':start_datex_dash
                           ,'datex_slash':start_datex_slash}
                  ,'end':{'datex':end_datex
                         ,'datex_dash':end_datex_dash
                         ,'datex_slash':end_datex_slash}
                  ,'curr':{'datex':curr_datex
                         ,'datex_dash':curr_datex_dash
                         ,'datex_slash':curr_datex_slash}
                  }
    return datex_dict



#########################################
### Execute if main
#########################################
if __name__ == '__main__':
    main()
