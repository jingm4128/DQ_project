# -*- coding: utf-8 -*-
"""
Created on Sun Apr  1 13:54:23 2018

@author: IBM
"""

GetData_config = {
                    'Quandl':
                        {
                         'Quandl_api_key':'GNw8NGcCx7Nsws6jzbMr',
                         'Quandl_partial_dir':'E:/Work/PartTime/DQ_Project/data/QuandlWiki/partial/',
                         'Quandl_col_names':['ticker','date','open','high','low','close','volume',  'exdividend','split_ratio', 'adj_open','adj_high','adj_low','adj_close', 'adj_volume']
                         },
                    
                    'AlphaVantage':
                        {
                        'AlphaVantage_api_key':'LF51W0ZIJO1GEGFN',
                        'AlphaVantage_query_timegap_sec':5,
                        'AlphaVantage_dir':'E:/Work/PartTime/DQ_Project/data/AlphaVantage/daily_adj/',
                        'AlphaVantage_col_names':['date', 'open', 'high', 'low', 'close', 'adj_close', 'volume','cdiv','split_coeff']
                        },
                    
                    'Secmaster':
                        {
                        'secm_dir':'E:/Work/PartTime/DQ_Project/data/Other/secmaster/',
                        'secm_col_names':['ticker','name','lastsale','mktcap_str','IPOyear','sector','industry','link'],
                        'secm_output_col_names':['date','exch','ticker','name','lastsale','mktcap','IPOyear','sector','industry']
                        },
                    
                    'Database':
                        {
                        'mysql_database':'us',
                        'mysql_hist_px_table_name':'us.equity_daily_hist_quandl',
                        'mysql_recent_px_table_name':'us.equity_daily_recent_alphav',
                        'mysql_secmaster_table_name':'us.secmaster'
                        }                    
                  }

ExecQuery_config = {
                    'mysql_conninfo': 
                        {
                        'host':'localhost',
                        'user':'root',
                        'passwd':'456123jj',
                        'connect_timeout':6000
                        },
                     'temp_data_dir':'E:/Work/PartTime/DQ_Project/data/Temp/'
                    }



RunGUI_config = {
                'data': 
                    {
                    'database':'us',
                    'px_dist_table':'us.px_dist',
                    'px_dist_conviction_table':'us.px_dist_conviction',
                    'px_series_table':'us.equity_daily_recent_alphav'
                    },
                
                'plot': 
                    {
                    'output_dir':'E:/Work/PartTime/DQ_Project/output/graphic/',
                    'tools':'pan,wheel_zoom,reset,save',
                    'description_html_file':'E:/Work/PartTime/DQ_Project/scripts/Python/Description.html',
                    'width':350,
                    'height':280,
                    'line_width':3.5
                    }
                }


ConstructPortfolio_config = {
                'data': 
                    {
                    'database':'us',
                    'weights_table':'us.weights_daily',
                    'px_dist_conviction_table':'us.px_dist_conviction',
                    'px_series_table':'us.equity_daily_recent_alphav'
                    },
                
                'portfolio': 
                    {
                    'output_dir':'E:/Work/PartTime/DQ_Project/output/graphic/',
                    'tools':'pan,wheel_zoom,reset,save',
                    'description_html_file':'E:/Work/PartTime/DQ_Project/scripts/Python/Description.html',
                    'width':350,
                    'height':280,
                    'line_width':3.5
                    }
                }