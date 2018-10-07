# -*- coding: utf-8 -*-
"""
Created on Sat Oct  6 22:42:12 2018

@author: IBM
"""

from scipy.optimize import fsolve
import math

def equations(p):
    x, y = p
    return (x+y**2-4, math.exp(x) + x*y - 3)

x, y =  fsolve(equations, (1, 1))