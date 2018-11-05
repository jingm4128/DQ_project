# -*- coding: utf-8 -*-
"""
Created on Sun Oct  7 10:00:34 2018

@author: IBM

"""

import numpy as np

def GetPdfMode(distribution_type, parameter_dict):
    if distribution_type == 'beta':
        a = parameter_dict['alpha']
        b = parameter_dict['beta']
        if a<0 or b<0:
            return np.nan()
        if a<=1 and b>=1 and a<b:
            return 0
        elif a>=1 and b<=1 and a>b:
            return 1
        elif a<1 and b<1:
            if a<=b: return 0 # can be 0 or 1
            else: return 1 # can be 0 or 1
        elif a==1 and b==1:
            return 0.5 # can be any number between 0 and 1, uniform dist
        elif a>1 and b>1:
            return (a-1)/(a+b-2)
        else:
            return np.nan()

