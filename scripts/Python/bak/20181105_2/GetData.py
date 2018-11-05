# -*- coding: utf-8 -*-
"""
Created on Mon Apr  1 10:46:11 2018

@author: Jing Ma
"""

#import numpy as np ## not used in this script for now
import pandas as pd
from datetime import datetime
#import sys
#import os
#import glob

import time
#import quandl ## later imported in the function
#import zipfile ## later imported in the function

from config import LoadData_config
from MyHelperLib import LogMeExit, GetDatexDict, ExecQuery

def main():
    specs = {
             'data_type':'crypto',
             'sub_data_type':'daily',
             'start_date':datetime.strptime('20181025','%Y%m%d'),
             'end_date':datetime.strptime('20181031','%Y%m%d'),
             'data_source':'AlphaVantage'
            }
    
    load_crypto = LoadData_Crypto(LoadData_config, specs)
    load_crypto.symbol_list
    load_crypto.GetSymbolList()
    
    load_crypto.DumpData(return_file_list_only=True)
    load_crypto.ProcessData(return_file_list_only=True)
    load_crypto.Load2DB(delete=True, return_query_only=True)
    
    
    

#########################################
### The Class
#########################################
    
class LoadData():
    def __init__(self, LoadData_config, specs):
        self.config = LoadData_config
        self.specs = specs
        self.datex_dict = GetDatexDict(specs['start_date'], specs['end_date'])
        self.dir = self.config[specs['data_type']][specs['sub_data_type']]['API'][specs['data_source']]['dir']
        self.raw_dir = self.dir +'raw/'
        self.proc_dir = self.dir +'proc/'
        self.raw_data_columns = self.config[self.specs['data_type']][self.specs['sub_data_type']]['API'][self.specs['data_source']]['raw_data_columns']
        self.db_columns = self.config[self.specs['data_type']][self.specs['sub_data_type']]['database']['db_columns']
        self.symbol_list = []
        self.raw_file_list = []
        self.proc_file_list = []
    
    def GetSymbolList(self):
        return self.symbol_list


    def DumpData(self, return_file_list_only=False):
        if self.specs['data_source'] not in self.config[self.specs['data_type']][self.specs['sub_data_type']]['API'].keys():
            LogMeExit('The data_source specified not supported - cound not find the API in config!','ERROR')
        
        if self.specs['data_source']=='NASDAQ_secmaster':
            import urllib
            base_url = self.config[self.specs['data_type']][self.specs['sub_data_type']]['API']['NASDAQ_secmaster']['base_url']
            
            for exchange in ['nasdaq','nyse','amex']:
                raw_file_name = self.raw_dir + '.'.join([exchange, self.datex_dict['curr']['datex'], 'csv'])
                self.raw_file_list.append(raw_file_name)
                urllib.request.urlretrieve (base_url.replace('<EXCH>',exchange), raw_file_name)
        
        
        if self.specs['data_source']=='AlphaVantage':
            import urllib
            base_url = self.config[self.specs['data_type']][self.specs['sub_data_type']]['API']['AlphaVantage']['base_url']
            query_wait_sec = self.config[self.specs['data_type']][self.specs['sub_data_type']]['API']['AlphaVantage']['query_wait_sec']
            
            i=1
            # dump data
            for symbol in self.GetSymbolList():
                LogMeExit('Round: '+str(i))
                LogMeExit('Duming symbol: '+symbol)
                i+=1
                raw_file_name = self.raw_dir + '.'.join([symbol,self.datex_dict['start']['datex'],self.datex_dict['end']['datex'],'csv'])
                data_file_url = base_url.replace('<SYMBOL>',symbol)
                LogMeExit('raw_file_name: '+raw_file_name)
                LogMeExit('data_file_url: '+data_file_url)
                try:
                    urllib.request.urlretrieve (data_file_url, raw_file_name)
                    self.raw_file_list.append(raw_file_name)
                except urllib.request.HTTPError:
                    LogMeExit('symbol '+ symbol + ' not availabe, skip!', 'WARN')
                    continue
                time.sleep(query_wait_sec)
            
        return self.raw_file_list  


    def ProcessData(self, return_file_list_only=False):
        return self.proc_file_list
    
    
    def Load2DB(self, delete=False, return_query_only=False):
        db_name = self.config[self.specs['data_type']][self.specs['sub_data_type']]['database']['db_name']
        delete_query = self.config[self.specs['data_type']][self.specs['sub_data_type']]['database']['delete_query']
        table_name = self.config[self.specs['data_type']][self.specs['sub_data_type']]['database']['table_name']
        
        queries = {}
        for f in self.proc_file_list:
            del_query = delete_query.replace('<TABLE_NAME>',table_name)
            del_query = del_query.replace('<START_DATE>',self.datex_dict['start']['datex'])
            del_query = del_query.replace('<END_DATE>',self.datex_dict['end']['datex'])
            LogMeExit('del_query: '+del_query)
            if delete and not return_query_only: ExecQuery(db_name, del_query)
            
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
            LogMeExit('load_query: '+load_query)
            queries[f] = {'del_query':del_query if delete else '','load_query':load_query}
            
        if not return_query_only: ExecQuery(db_name, load_query)
        return queries



class LoadData_Equity(LoadData):
    #def __init__(self): pass
    def GetSymbolList(self):
        secmaster_table_name = self.config[self.specs['data_type']][self.specs['sub_data_type']]['database']['secmaster_table_name']
        db_name = self.config[self.specs['data_type']][self.specs['sub_data_type']]['database']['db_name']
        universe = self.config[self.specs['data_type']][self.specs['sub_data_type']]['database']['universe']
        
        get_symbols_query = """ select distinct symbol 
                                from """+secmaster_table_name+ """
                                where date in (select max(date) from """+secmaster_table_name+ """)
                                #and sector='Health Care'
                                order by marketCap desc limit """ + universe + """
                                ;"""
        LogMeExit('The Query: \n' + get_symbols_query)
        symbol_lol = ExecQuery(db_name,get_symbols_query, True)
        self.symbol_list = [i[0] for i in symbol_lol]
        return self.symbol_list
    
    def ProcessData(self, return_file_list_only=False):
        data_df_list = []
        if self.specs['sub_data_type'] == 'secmaster':
            for raw_file_name in self.raw_file_list:
                data = pd.read_csv(raw_file_name, header=1, names = self.raw_data_columns, index_col=False) #header=None #if there is no header
                data['date'] = self.datex_dict['curr']['datex_slash']
                data['exch'] = (raw_file_name.split('/')[-1]).split('.')[0]
                data['mktcap_unit'] = 1e6*(data['mktcap_str'].str[-1]=='M') + 1e9*(data['mktcap_str'].str[-1]=='B')
                data['mktcap_num'] = (data['mktcap_str'].str[1:-1]).astype(float)
                data['mktcap'] = data['mktcap_num']*data['mktcap_unit']
                
                data_df_list.append(data[ self.db_columns ])
            
            agg_data = pd.concat(data_df_list, ignore_index=True)
            proc_file_name = self.proc_dir + 'proc.' + self.datex_dict['curr']['datex'] + '.' + self.datex_dict['curr']['datex'] + '.csv'
            self.proc_file_list = [proc_file_name]
            agg_data.to_csv(proc_file_name, na_rep='NULL', index=False, header=None)       
            
        
        elif self.specs['sub_data_type'] == 'daily':
            i=1
            for raw_file_name in self.raw_file_list:
                #raw_file_name = raw_file_list[1] ###DEBUG
                #keep_lastest=True ###DEBUG
                symbol = (raw_file_name.split('/')[-1]).split('.')[0]
                LogMeExit('Round: '+str(i))
                LogMeExit('Processing symbol: '+symbol)
                i+=1
                # read the data
                try:
                    data = pd.read_csv(raw_file_name, header=0, names = self.raw_data_columns, index_col=False) 
                except pd.errors.ParserError:
                    print('ERROR: Could not parse the data in: ' + raw_file_name)
                    continue
                except FileNotFoundError:
                    print('ERROR: Could not find the file: ' + raw_file_name)
                    continue
                
                # only keep the data when date = date in the file name
                data = data[data['date'] >= self.datex_dict['start']['datex_dash']]
                data = data[data['date'] <= self.datex_dict['end']['datex_dash']]
                
                # transform the format of the data
                data['date'] = pd.to_datetime(data['date']).dt.strftime('%Y/%m/%d')
                data['symbol'] = symbol
                data_df_list.append(data[ self.db_columns ])
            
            agg_data = pd.concat(data_df_list, ignore_index=True)
            # generate the file name based on the raw file name
            proc_file_name = self.proc_dir + '.'.join(['proc',self.datex_dict['start']['datex'],self.datex_dict['end']['datex'],'csv'])
            
            # output with nan being 'NULL'
            agg_data.to_csv(proc_file_name, na_rep='NULL', index=False, header=None)       
            
            # update the dict
            self.proc_file_list.append(proc_file_name)
            
        elif self.specs['sub_data_type'] == 'minute':
            LogMeExit('The sub_data_type minute is not supported yet, skip!', 'WARN')
        else:
            LogMeExit('The sub_data_type '+self.specs['sub_data_type']+' is not supported yet, skip!', 'WARN')

        return self.proc_file_list



class LoadData_Crypto(LoadData):
    #def __init__(self): pass
    def GetSymbolList(self):
        self.symbol_list = self.config[self.specs['data_type']][self.specs['sub_data_type']]['database']['pairs_dict'].keys()
        return self.symbol_list

    def ProcessData(self, return_file_list_only=False):
        data_df_list = []
        i=1
        for raw_file_name in self.raw_file_list:
            #raw_file_name = raw_file_list[1] ###DEBUG
            #keep_lastest=True ###DEBUG
            symbol = (raw_file_name.split('/')[-1]).split('.')[0]
            LogMeExit('Round: '+str(i))
            LogMeExit('Processing symbol: '+symbol)
            i+=1
            # read the data
            try:
                data = pd.read_csv(raw_file_name, header=0, names = self.raw_data_columns, index_col=False) 
            except pd.errors.ParserError:
                LogMeExit('Could not parse the data in: ' + raw_file_name + ', skip!','WARN')
                continue
            
            # only keep the data when date = date in the file name
            data = data[data['date'] >= self.datex_dict['start']['datex_dash']]
            data = data[data['date'] <= self.datex_dict['end']['datex_dash']]
            
            # transform the format of the data
            data['date'] = pd.to_datetime(data['date']).dt.strftime('%Y/%m/%d')
            data['symbol'] = symbol
            data_df_list.append(data[ self.db_columns ])
        
        agg_data = pd.concat(data_df_list, ignore_index=True)
        # generate the file name based on the raw file name
        proc_file_name = self.proc_dir + '.'.join(['proc',self.datex_dict['start']['datex'],self.datex_dict['end']['datex'],'csv'])
        
        # output with nan being 'NULL'
        agg_data.to_csv(proc_file_name, na_rep='NULL', index=False, header=None)       
        
        # update the dict
        self.proc_file_list.append(proc_file_name)
    
        return self.proc_file_list






#########################################
### Execute if main
#########################################
if __name__ == '__main__':
    main()
