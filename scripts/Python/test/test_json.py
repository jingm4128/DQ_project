# -*- coding: utf-8 -*-
"""
Created on Mon Apr  2 22:16:11 2018

@author: IBM
"""

import urllib

url1 = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=MSFT&apikey=demo&datatype=csv'

urllib.request.urlretrieve (url1, "MSFT.csv")