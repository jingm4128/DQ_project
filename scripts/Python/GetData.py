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
    secm_data_dir = GetData_config['Secmaster']['secm_dir']
    secm_col_names = GetData_config['Secmaster']['secm_col_names']
    secm_output_col_names = GetData_config['Secmaster']['secm_output_col_names']
    data_dir = GetData_config['AlphaVantage']['AlphaVantage_dir']
    api_key = GetData_config['AlphaVantage']['AlphaVantage_api_key']
    api_query_timegap_sec = GetData_config['AlphaVantage']['AlphaVantage_query_timegap_sec']
    col_names = GetData_config['AlphaVantage']['AlphaVantage_col_names']
    database = GetData_config['Database']['mysql_database']
    px_table_name = GetData_config['Database']['mysql_recent_px_table_name']
    secmaster_table_name = GetData_config['Database']['mysql_secmaster_table_name']
    daily_data_universex = GetData_config['Database']['daily_data_universex']
    
    raw_dir = data_dir + 'raw/'
    proc_dir = data_dir + 'proc/'
    
    #datex_dict = GetDatexDict(datetime.now())
    # create different format for the start and enc date to load
    datex_dict = GetDatexDict(datetime.strptime('20180727','%Y%m%d')
                            , datetime.strptime('20171005','%Y%m%d'))
    
    # load the latest secmaster
    if True:
        print('dumping/processing/loading secmaster data...')
        secm_proc_file_dict = DumpProcSecmasterData(secm_data_dir, secm_col_names, secm_output_col_names,datex_dict)
        LoadData(secm_proc_file_dict, database, secmaster_table_name, True)
    
    # Get the list of tickers
    ticker_list = GetTickerList(secmaster_table_name, database, daily_data_universex)
    
    # Download the price/volume data from AlphaVantage
    print('dumping prices data...')
    raw_file_list = DumpDailyDataFromAlphav(raw_dir, api_key, api_query_timegap_sec, ticker_list, datex_dict, False)
    #print(raw_file_list)
    
    # Process the data downloaded
    print('processing prices data...')
    proc_file_list = ProcessDailyAlphavData(proc_dir, raw_file_list, col_names, datex_dict, True)
    #print(proc_file_list)
    
    # Load the data to the database
    print('loading prices data...')
    LoadData(proc_file_list, database, px_table_name, datex_dict, True)
    
    
    ### dump minbucket data
    
    #historical
    #ProcessData('E:/Work/PartTime/DQ_Project/data/QuandlWiki/hist/proc/',['E:/Work/PartTime/DQ_Project/data/QuandlWiki/hist/raw/WIKI_PRICES.csv'], col_names)
    #LoadData(['E:/Work/PartTime/DQ_Project/data/QuandlWiki/hist/proc/proc_WIKI_PRICES.csv'], database, table_name)
    
    
    
    


#########################################
### Functions
#########################################

### 0. Secmaster Data ###########
### 0.1 Dump/Proc Data
def DumpProcSecmasterData(secm_data_dir, secm_col_names, secm_output_col_names,datex_dict):
    # 1) dump data
    import urllib
    url_base = 'https://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=<EXCH>&render=download'
    datex = datex_dict['curr']['datex']
    raw_file_list = []
    
    for exchange in ['nasdaq','nyse','amex']:
        raw_file_name = secm_data_dir + 'raw/' + '.'.join([exchange, datex, 'csv'])
        raw_file_list.append(raw_file_name)
        data_file_url = url_base.replace('<EXCH>',exchange)
        urllib.request.urlretrieve (data_file_url, raw_file_name)
    
    # 2) process data
    data_df_list = []
    
    for raw_file_name in raw_file_list:
        data = pd.read_csv(raw_file_name, header=1, names = secm_col_names, index_col=False) #header=None #if there is no header
        data['date'] = datex_dict['curr']['datex_slash']
        data['exch'] = (raw_file_name.split('/')[-1]).split('.')[0]
        data['mktcap_unit'] = 1e6*(data['mktcap_str'].str[-1]=='M') + 1e9*(data['mktcap_str'].str[-1]=='B')
        data['mktcap_num'] = (data['mktcap_str'].str[1:-1]).astype(float)
        data['mktcap'] = data['mktcap_num']*data['mktcap_unit']
        
        data_df_list.append(data[secm_output_col_names])
    
    agg_data = pd.concat(data_df_list, ignore_index=True)
    proc_file_name = secm_data_dir + 'proc/' + 'proc.' + datex + '.csv'
    proc_file_dict = {proc_file_name:datex}
    agg_data.to_csv(proc_file_name, na_rep='NULL', index=False, header=None)       
    return proc_file_dict

### 0.2 Get the ticker list
def GetTickerList(secmaster_table_name, database, universex):
    get_tickers_query = """ select distinct ticker 
                            from """+secmaster_table_name+ """
                            where date in (select max(date) from """+secmaster_table_name+ """)
                            #and sector='Health Care'
                            order by marketCap desc limit """ + universex + """
                            ;"""
    print(get_tickers_query)
    ticker_lol = ExecQuery(database,get_tickers_query, True)
    ticker_list = [i[0] for i in ticker_lol]
    return ticker_list


### 1. Dump Data ###########
### 1.1 From Quandl (deprecated)
def DumpBulkDataFromQuandl(raw_dir, api_key):  
    # defininations
    zip_file_name = raw_dir + datetime.strftime(datetime.now(),'%Y%m%d.%H%M%S') + '.zip'
    
    # bulkdownload - zip
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
    
    # does not know the names of the unzipped files, so we have to find out
    raw_file_list = glob.glob(raw_dir + '*.csv')
    raw_file_list = [f.replace('\\','/') for f in raw_file_list]
    return raw_file_list


### 1.2 From AlphaVantage - Daily (current)
def DumpDailyDataFromAlphav(raw_dir, api_key, api_query_timegap_sec, ticker_list, datex_dict, clear_dir=False):
    import urllib
    
    data_set = 'TIME_SERIES_DAILY_ADJUSTED'
    #outputsize = 'full'
    outputsize = 'compact'
    url_base = 'https://www.alphavantage.co/query?' +'outputsize='+outputsize+'&'
    start_datex = datex_dict['start']['datex']
    end_datex = datex_dict['end']['datex']
    raw_file_list = []
    
    # clear the dir
    if clear_dir:
        for f in glob.glob(raw_dir + '*.csv'): os.remove(f)
    
    i=1
    # dump data
    for t in ticker_list:
        print(t)
        print(i)
        i+=1
        raw_file_name = raw_dir + '.'.join([t,start_datex,end_datex,'csv'])
        data_file_url = url_base+'function='+data_set+'&symbol='+t+'&apikey='+api_key+'&datatype=csv'
        print(data_file_url)
        try:
            urllib.request.urlretrieve (data_file_url, raw_file_name)
            raw_file_list.append(raw_file_name)
        except urllib.request.HTTPError:
            #AXON
            print('ticker '+ t + ' not availabe, skip!')
            continue
        time.sleep(api_query_timegap_sec)
    
    return raw_file_list

### 1.3 From AlphaVantage - Minute (current)
def DumpMinuteDataFromAlphav(raw_dir, api_key, api_query_timegap_sec, ticker_list, datex_dict, clear_dir=False):
    pass


### 2. ProcessData ######################
### 2.1 Process Quandl data (deprecated)
def ProcessQuandlData(proc_dir, raw_file_list, col_names, datex_dict, keep_lastest=False):
    proc_file_list = []
    for raw_file_name in raw_file_list:
        raw_file_name = raw_file_list[0] ###DEBUG
        #keep_lastest=True ###DEBUG
        
        # read the data
        data = pd.read_csv(raw_file_name, header=None, names = col_names, index_col=False)
        #data = pd.read_csv(raw_file_name) ###DEBUG, hist
        
        if keep_lastest:
            # only keep the data when date = date in the file name
            data = data[data['date'] >= datex_dict['start']['datex_dash']]
            data = data[data['date'] <= datex_dict['end']['datex_dash']]
        
        # transform the format of the data
        data['date'] = pd.to_datetime(data['date']).dt.strftime('%Y/%m/%d')
                
        # generate the file name based on the raw file name
        proc_file_name = proc_dir + 'proc_' + raw_file_name.split('/')[-1]
        
        # output with nan being 'NULL'
        data.to_csv(proc_file_name, na_rep='NULL', index=False, header=None)
        
        proc_file_list.append(proc_file_name)
    
    return proc_file_list


### 2.2 Process AlphaVantage data - Daily (deprecated)
def ProcessDailyAlphavData(proc_dir, raw_file_list, col_names, datex_dict, keep_lastest=False):
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
            data = pd.read_csv(raw_file_name, header=0, names = col_names, index_col=False) 
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
        data_df_list.append(data[ ['ticker']+col_names ])
    
    agg_data = pd.concat(data_df_list, ignore_index=True)
    # generate the file name based on the raw file name
    proc_file_name = proc_dir + '.'.join(['proc',start_datex,end_datex,'csv'])
    
    # output with nan being 'NULL'
    agg_data.to_csv(proc_file_name, na_rep='NULL', index=False, header=None)       
    
    # update the dict
    proc_file_list.append(proc_file_name)
    return proc_file_list


### 2.3 Process AlphaVantage data - Minute (deprecated)
def ProcessMinuteAlphavData(proc_dir, raw_file_list, col_names, datex_dict, keep_lastest=False):
    pass


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



#########################################
### Examples/Explanations
#########################################
def DumpDfDataFromQuandl(sd, ed, ticker):  
    # bulkdownload
    import quandl
    quandl.ApiConfig.api_key = GetData_config['Quandl']['Quandl_api_key']
    df = quandl.get_table('WIKI/PRICES'
                          , qopts = {'columns': ['ticker', 'date', 'adj_close']}
                          , date={'gte': sd, 'lte': ed}
                          , ticker=ticker
                          , paginate=True)
    return df

def DumpDataFromQuandl_example():
    import quandl
    
    ### Here are a few ways to dump the data from Quandl, to data frame
    # 0. load the api_key
    quandl.ApiConfig.api_key = GetData_config['Quandl']['Quandl_api_key']
    
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

def DumpDataFromAlphaV_example(sd, ed, ticker):  
    import urllib
    
    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=MSFT&apikey=demo&datatype=csv'
    urllib.request.urlretrieve (url, "MSFT2.csv")
