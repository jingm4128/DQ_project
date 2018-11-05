# -*- coding: utf-8 -*-
"""
Created on Sun Apr  1 13:54:23 2018

@author: Jing Ma
"""

Basic_config = {
	'logs':{
		'log_dir':'E:/Work/PartTime/DQ_Project/logs/',
		'default_log_name':'DQ_log_<TODAY_YYYYMMDD>.txt'
	}
}


LoadData_config = {
    'us_eqy': # data type
    {
        'secmaster': #sub_data_type
        {
            'API':
            {
                'NASDAQ_secmaster':
                {
                    'api_key':None,
                    'base_url':'https://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=<EXCH>&render=download',
                    'query_wait_sec':0,
                    'dir':'E:/Work/PartTime/DQ_Project/data/Other/secmaster/',
                    'raw_data_columns':['ticker','name','lastsale','mktcap_str','IPOyear','sector','industry','link']
                }
            },
            'database':
            {
                'db_type':'mysql', # not used now, for future improvements
                'db_name':'us',
                'table_name':'us.secmaster',
                'secmaster_table_name':'us.secmaster',
                'universe':'5000',
                'db_columns':['date','exch','ticker','name','lastsale','mktcap','IPOyear','sector','industry'],
				'delete_query':'delete from <TABLE_NAME> where date>=<START_DATE> and date<=<END>; commit;',
				'additional_query':None
            }
        },
        'daily':
        {
            'API':
            {
                'Quandl':
                {
                    'api_key':'GNw8NGcCx7Nsws6jzbMr',
                    'base_url':None,
                    'query_wait_sec':0,
                    'dir':'E:/Work/PartTime/DQ_Project/data/QuandlWiki/partial/',
                    'raw_data_columns':['ticker','date','open','high','low','close','volume','exdividend','split_ratio'
                                        ,'adj_open','adj_high','adj_low','adj_close', 'adj_volume']
                },
                'AlphaVantage':
                {
                    'api_key':'LF51W0ZIJO1GEGFN',
                    'base_url':'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&outputsize=compact%apikey=LF51W0ZIJO1GEGFN&symbol=<SYMBOL>&datatype=csv',
                    'query_wait_sec':20,
                    'dir':'E:/Work/PartTime/DQ_Project/data/AlphaVantage/daily_adj/',
                    'raw_data_columns':['date','open','high','low','close','adj_close','volume','cdiv','split_coeff']
                }
            },
            'database':
            {
                'db_type':'mysql', # not used now, for future improvements
                'db_name':'us',
                'table_name_hist':'us.equity_daily_hist_quandl',
                'table_name':'us.equity_daily_recent_alphav',
                'secmaster_table_name':'us.secmaster',
                'universe':'480',
                'db_columns':['ticker','date','open','high','low','close','adj_close','volume','cdiv','split_coeff'],
				'delete_query':'delete from <TABLE_NAME> where date>=<START_DATE> and date<=<END>; commit;',
				'additional_query':None
            }
        },
        'minute':None,
        'tick':None
    },
    
    'crypto': # data type
    {
        'secmaster':None,
        'daily':
        {
            'API':
            {
                'AlphaVantage':
                {
                    'api_key':'LF51W0ZIJO1GEGFN',
                    'base_url':'https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&apikey=LF51W0ZIJO1GEGFN&symbol=<SYMBOL>&market=USD&datatype=csv',
                    'query_wait_sec':20,
                    'dir':'E:/Work/PartTime/DQ_Project/data/AlphaVantage/cypto_daily_adj/',
                    'raw_data_columns':['date','open','high','low','close','open','high','low','close','volume','mkt_cap']
                }
            },
            'database':
            {
				'db_name':'crypto',
				'table_name_hist':'crypto.daily_hist_alphav',
				'table_name':'crypto.daily_recent_alphav',
				'secmaster_table_name':None,
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
				'db_columns':['ticker','date','open','high','low','close','volume'],
				'delete_query':'delete from <TABLE_NAME> where date>=<START_DATE> and date<=<END>; commit;',
				'additional_query':None
            }
        },
        'minute':None,
        'tick':None
    },
    
    'asia_eqy': None, # data type
    'fut': None, # data type
    'option': None, # data type

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
