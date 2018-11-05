# -*- coding: utf-8 -*-
"""
Created on Sat Nov  3 11:59:10 2018

@author: IBM
"""


##################################################################################
### The I/O Related Functions
##################################################################################
from datetime import datetime
import sys
from config import Basic_config

#LogMeExit('test','OTHER',1,'other')

def LogMeExit(msg_to_log, msg_type='INFO', lines_above=0, mode='both', to_exit=False):
    """
    LogMeExit(msg_to_log, msg_type='INFO', mode='both', to_exit=False)
    
    Description:
        take the message to log, and other parameters and then print and/or log it to a files (always append)
    
    Parameters:
        mode <print|to_file|both>
        msg_type <INFO|WARN|ERROR>
    
    Output:
        None
    """
    
    datex_dict = GetDatexDict()
    curr_datetx = datex_dict['curr']['datex']
    prepend_timex = datex_dict['curr']['datetimex_standard'] + '\t'
    
    msg_list = []
    msg_list.append('\n'*int(lines_above) + prepend_timex + msg_type + ': ' + msg_to_log)
    
    if msg_type not in ['INFO','WARN','ERROR']:
        msg_list.append(prepend_timex + 'WARN: '+msg_type+' is not a standard msg_type <INFO|WARN|ERROR> for function LogMeExit(*)')
    if mode not in ['print','to_file','both']:
        msg_list.append(prepend_timex + 'WARN: '+mode+' is not a expected mode <print|to_file|both> for function LogMeExit(*)')
    if mode not in ['print','to_file','both']:
        msg_list.append(prepend_timex + 'WARN: '+mode+' is not a expected mode <print|to_file|both> for function LogMeExit(*)')
    
    
    if mode not in ['to_file']:
        for msg in msg_list: print(msg)
    if mode not in ['print']:
        log_file = Basic_config['logs']['log_dir'] + Basic_config['logs']['default_log_name'].replace('<TODAY_YYYYMMDD>',curr_datetx)
        print(log_file)
        with open(log_file, "a") as f:
            for msg in msg_list:
                f.write(msg+'\n')
    
    if to_exit: sys.exit()






##################################################################################
### The MySQL Related Functions
##################################################################################
    
import MySQLdb #mysqlclient
import pandas as pd
#from datetime import datetime

from config import ExecQuery_config
host = ExecQuery_config['mysql_conninfo']['host']
user = ExecQuery_config['mysql_conninfo']['user']
passwd = ExecQuery_config['mysql_conninfo']['passwd']
temp_data_dir = ExecQuery_config['temp_data_dir']

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





##################################################################################
### Other helper functions
##################################################################################
def GetDatexDict(start_date=datetime.now(), end_date=datetime.now()):
    """
    GetDatexDict(start_date=datetime.now(), end_date=datetime.now())
    
    """
    now = datetime.now()
    
    curr_datex = datetime.strftime(now,'%Y%m%d')
    curr_datex_dash = '-'.join([curr_datex[:4],curr_datex[4:6],curr_datex[6:8]])
    curr_datex_slash = '/'.join([curr_datex[:4],curr_datex[4:6],curr_datex[6:8]])
    
    
    curr_datetimex = datetime.strftime(now,'%Y%m%d.%H%M%S.%f')
    curr_datetimex_hms = datetime.strftime(now,'%Y%m%d.%H%M%S')
    curr_datetimex_hm = datetime.strftime(now,'%Y%m%d.%H%M')
    curr_datetimex_standard = datetime.strftime(now,'%Y%m%d %H:%M:%S.%f')
    
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
                         ,'datex_slash':curr_datex_slash
                         ,'datetimex':curr_datetimex
                         ,'datetimex_hms':curr_datetimex_hms
                         ,'datetimex_hm':curr_datetimex_hm
                         ,'datetimex_standard':curr_datetimex_standard}
                  }
    return datex_dict