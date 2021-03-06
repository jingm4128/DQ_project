# -*- coding: utf-8 -*-
"""
Created on Sun Apr  1 13:54:23 2018

@author: Jing Ma
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
                        'api_key':'LF51W0ZIJO1GEGFN',
                        'query_timegap_sec':20,
                        'dir':
                                {'us_eqy_daily':'E:/Work/PartTime/DQ_Project/data/AlphaVantage/daily_adj/',
                                 'crypto':'E:/Work/PartTime/DQ_Project/data/AlphaVantage/cypto_daily_adj/'
                                },
                        'raw_data_columns':
                                {'us_eqy_daily':['date','open','high','low','close','adj_close','volume','cdiv','split_coeff'],
                                 'crypto':['date','open','high','low','close','open','high','low','close','volume','mkt_cap']
                                }
                        },
                    
                    'Secmaster':
                        {
                        'secm_dir':'E:/Work/PartTime/DQ_Project/data/Other/secmaster/',
                        'secm_col_names':['ticker','name','lastsale','mktcap_str','IPOyear','sector','industry','link'],
                        'secm_output_col_names':['date','exch','ticker','name','lastsale','mktcap','IPOyear','sector','industry']
                        },
                    
                    'Database':
                        {
                        'us_eqy':
                            {
                            'db_type':'mysql', # not used now, for future improvements
                            'database':'us',
                            'mysql_hist_px_table_name':'us.equity_daily_hist_quandl',
                            'mysql_recent_px_table_name':'us.equity_daily_recent_alphav',
                            'mysql_secmaster_table_name':'us.secmaster',
                            'daily_data_universex':'480',
                            'db_columns':['ticker','date','open','high','low','close','adj_close','volume','cdiv','split_coeff']
                            },
                        'crypto':
                            {
                            'db_type':'mysql', # not used now, for future improvements
                            'database':'crypto',
                            'mysql_hist_px_table_name':'crypto.daily_hist_alphav',
                            'mysql_recent_px_table_name':'crypto.daily_recent_alphav',
                            'mysql_secmaster_table_name':None,
                            'pairs_dict':{'BTC-USD':{'symbol':'BTC','market':'USD'},
                                          'ETH-USD':{'symbol':'ETH','market':'USD'},
                                          'LTC-USD':{'symbol':'LTC','market':'USD'},
                                          'ETC-USD':{'symbol':'ETC','market':'USD'},
                                          'USDT-USD':{'symbol':'USDT','market':'USD'},
                                          'XRP-USD':{'symbol':'XRP','market':'USD'},
                                          'BCH-USD':{'symbol':'BCH','market':'USD'},
                                          'NEO-USD':{'symbol':'NEO','market':'USD'},
                                          'EOS-USD':{'symbol':'EOS','market':'USD'},
                                          'DASH-USD':{'symbol':'DASH','market':'USD'}
                                         },
                            'db_columns':['ticker','date','open','high','low','close','volume']
                            }
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
                    'px_beta_dist_table':'us.px_beta_dist',
                    'px_dist_conviction_table':'us.px_dist_conviction',
                    'px_series_table':'us.equity_daily_recent_alphav'
                    },
                
                'plot': 
                    {
                    'output_dir':'E:/Work/PartTime/DQ_Project/output/graphic/',
                    'tools':'pan,wheel_zoom,reset,save',
                    'description_html_file':'E:/Work/PartTime/DQ_Project/scripts/Python/Description.html',
                    'width':350,
                    'height':500,
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
