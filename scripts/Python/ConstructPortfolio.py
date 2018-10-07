# -*- coding: utf-8 -*-
"""
Created on Sat May  5 00:17:58 2018

@author: IBM


There will be several choices in the portfolio optimization
1. Equaly weighted
2. Randomly weighted
3. Market weighted (not ready yet)
4. Volume weighted
3. Mean-variance optimizaion (not ready yet)
4. Black-Litterman optimizaion (not ready yet)
5. Risk Parity (not ready yet)
"""


import pandas as pd
import numpy as np
import random
from datetime import datetime
from statsmodels.stats.correlation_tools import cov_nearest

from ExecQuery import ExecQuery, LoadDataFrame2DB
from config import ConstructPortfolio_config
database = ConstructPortfolio_config['data']['database']
weights_table = ConstructPortfolio_config['data']['weights_table']
px_series_table = ConstructPortfolio_config['data']['px_series_table']

def main():
    GetPortfolio()


def GetPortfolio():
    universe_list = ['AAPL','IBM','C','BABA','JNJ']
    start_datex = '20180101'
    end_datex = '20180504'
    query = """ select date, ticker, adj_close as price, adj_close*volume as volume
                from """ + px_series_table + """
                where ticker in ('""" + "', '".join(universe_list) + """')
                and date >= '""" + start_datex +"""' 
                and date <= '""" + end_datex + """'
                order by ticker, date
            ;"""
    input_df = ExecQuery(database, query, fetch_data = True, to_dataframe = True)
    input_df['return'] = input_df.groupby('ticker')['price'].pct_change()

    cp_1 = ConstructPortfolio(input_df)
    
    print(cp_1)
    print(cp_1.ticker_attrs_df)
    print(cp_1.GetEqualWeightedPortfolio())
    print(cp_1.GetRandomWeightedPortfolio())
    print(cp_1.GetVolumeWeightedPortfolio())
    print(cp_1.GetMeanVariancePortfolio())
    #print(cp_1.GetBlackLittermanPortfolio())
    #print(cp_1.GetRiskParityPortfolio())


#########################################
### The Class
#########################################
class ConstructPortfolio:
    """
    1) input
        strategy -- the name of the strategy
        df of 
            date (date for daily, update later to add the usage of minutes)
            ticker
            price
            return
            volume
    
    2) output
            df of 
            ticker
            weight
    3) 
    """
    exp_ret = 0.05
    
    def __init__(self, input_df):
        #input_df should have 'date', 'ticker', 'return'
        self.input_df = input_df
        self.ticker_attrs_df = input_df.groupby(['ticker'], as_index=False).mean()[['ticker', 'return','volume']]
        self.max_date = input_df['date'].max()
    
    
    def GetEqualWeightedPortfolio(self):
        self.weights_df = (self.ticker_attrs_df[['ticker']]).copy()
        self.weights_df['date'] = self.max_date
        self.weights_df['strategy'] = 'EW'
        self.weights_df['weights'] = 1/len(self.weights_df)
        return self.weights_df[['strategy', 'date','ticker','weights']]
        
    
    def GetRandomWeightedPortfolio(self):
        self.weights_df = (self.ticker_attrs_df[['ticker']]).copy()
        self.weights_df['date'] = self.max_date
        self.weights_df['strategy'] = 'RW'
        self.weights_df['weights'] = pd.Series(random.sample(range(1, 100), len(self.weights_df)))
        self.weights_df['weights'] = self.weights_df['weights']/(self.weights_df['weights'].sum())
        return self.weights_df[['strategy', 'date','ticker','weights']]
      
        
    def GetVolumeWeightedPortfolio(self):
        self.weights_df = (self.ticker_attrs_df[['ticker','volume']]).copy()
        self.weights_df['date'] = self.max_date
        self.weights_df['strategy'] = 'VW'
        self.weights_df['weights'] = self.weights_df['volume']/(self.weights_df['volume'].sum())
        return self.weights_df[['strategy', 'date','ticker','weights']]


    def GetMeanVariancePortfolio(self):
        self.weights_df = (self.ticker_attrs_df[['ticker']]).copy()
        self.weights_df['date'] = self.max_date
        self.weights_df['strategy'] = 'MV'
        self.weights_df['weights'] = self.GetEqualWeightedPortfolio()['weights']
        
        pivot_input_df = (self.input_df[['date','ticker','return']]).pivot(index='date', columns='ticker', values='return')
        pivot_input_df = pivot_input_df.dropna(axis=0, how='any')
        print(pivot_input_df)
        

        #self.weights_df['weights'] = 0
        return self.weights_df[['strategy', 'date','ticker','weights']]
    
    
    def GetBlackLittermanPortfolio(self):
        self.weights_df = (self.ticker_attrs_df[['ticker']]).copy()
        self.weights_df['date'] = self.max_date
        self.weights_df['strategy'] = 'BL'
        self.weights_df['weights'] = 0
        return self.weights_df[['strategy', 'date','ticker','weights']]
    
    
    def GetRiskParityPortfolio(self):
        self.weights_df = (self.ticker_attrs_df[['ticker']]).copy()
        self.weights_df['date'] = self.max_date
        self.weights_df['strategy'] = 'RP'
        self.weights_df['weights'] = 0
        return self.weights_df[['strategy', 'date','ticker','weights']]


    def PortfolioVar(cov, weights):
        var = (weights * cov * weights.T).sum()
        return var




#########################################
### The Helper Functions
#########################################
def LoadWeights2DB(database, weights_df, weights_table):
    weights_df_cp = weights_df.copy()
    weights_df_cp['date'] = pd.to_datetime(weights_df_cp['date']).dt.strftime('%Y/%m/%d')
    weights_df_cp['asof_datetime'] = (datetime.now()).strftime('%Y/%m/%d %H:%M:%S')
    LoadDataFrame2DB(database, weights_df_cp[['asof_datetime','strategy', 'date','ticker','weights']], weights_table)





######################################
### Execute if main
######################################
if __name__ == '__main__':
    main()