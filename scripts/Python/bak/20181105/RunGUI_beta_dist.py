# -*- coding: utf-8 -*-
"""
Created on Sat Oct  7 00:25:47 2018
Last modified on 20181007 - added comments

@author: Jing Ma

    bokeh serve E:\Work\PartTime\DQ_project\scripts\Python\RunGUI_beta_dist.py
at your command prompt. Then navigate to the URL
    http://localhost:5006/RunGUI_beta_dist.py
in your browser.

This version does the interpolation/inference ***based on the beta distribution***, and plot the following
1) the distribution based on the three input
    - price_mode: most expected price (the mode for the beta distribution)
    - price_ban: the price band width (the difference between the max possible price and the min possible price)
    - price_skew: the skew between -1 and 1 (-1 when the min possible price would be the most possible price, and 1 for the max possible price)
    - price_shape: between 0 and 1, the larger it is the more steep the shape of the pdf is, and the smaller the more flat
2) the auto distribution
    - the price distribution that is pre-set
3) the market price_volume data

"""


import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import gridplot, widgetbox
from bokeh.models import Range1d, LinearAxis, ColumnDataSource, PrintfTickFormatter, DatetimeTickFormatter, HoverTool, Div
from bokeh.models.widgets import Slider, TextInput, Button
from bokeh.plotting import figure
from os.path import dirname, join



from RunGUI_help import CanToFloat, QueryGUIData, InsertPxBetaDist, InsertPxDistConviction
from config import RunGUI_config
data_config = RunGUI_config['data']
plot_config = RunGUI_config['plot']

ticker = 'JNJ' #initialize

# The descriptions
desc = Div(text=open(join(dirname(__file__), plot_config['description_html_file'])).read(), width=2*plot_config['width'])

# Set up the px_series_fig
px_series_results = QueryGUIData(data_config, ticker, 'px_series')
px_series_df = px_series_results['df']
volume_unit_str = px_series_results['volume_unit_str']
px_series_source = ColumnDataSource(data=dict(price=px_series_df['price'], volume=px_series_df['volume'], date=px_series_df['date']))

px_series_hover = HoverTool(tooltips=[("date", "@date{%F}"),("price", "$@{price}{%0.2f}")]
                           , formatters={'date':'datetime','price':'printf'})
plot_options = dict(width=int(2.9*plot_config['width']), plot_height=plot_config['height'])
px_series_fig = figure(**plot_options, x_axis_type="datetime", title = "Price Volume Time Series", tools=[px_series_hover])
px_series_fig.xaxis.formatter=DatetimeTickFormatter(days='%Y/%m/%d',
                                                    months='%Y/%m/%d',
                                                    hours='%Y/%m/%d',
                                                    #hours='%Y/%m/%d %H:%M',
                                                    minutes='%Y/%m/%d')
px_series_fig.y_range = Range1d(start=0.95*px_series_df['price'].min(), end=1.05*px_series_df['price'].max())
px_series_fig.extra_y_ranges = {"volume": Range1d(start=0, end=1.2*px_series_df['volume'].max())}
px_series_fig.add_layout(LinearAxis(y_range_name='volume'), 'right')
px_series_fig.yaxis[1].formatter = PrintfTickFormatter(format="%5.1f " + volume_unit_str)

px_series_fig.line('date', 'price', source=px_series_source, line_width=plot_config['line_width'], color='olivedrab', alpha=0.9)
px_series_fig.vbar(bottom=0, top='volume', x='date', source=px_series_source, width=1.5, color='grey', alpha=0.5, y_range_name='volume')


# Set up the px_beta_dist_auto_fig
px_beta_dist_auto_df = QueryGUIData(data_config, ticker, 'px_beta_dist_autom')
px_beta_dist_auto_source = ColumnDataSource(data=dict(price=px_beta_dist_auto_df['price'], prob=px_beta_dist_auto_df['prob']))
px_beta_dist_auto_hover = HoverTool(tooltips=[("price", "$@{price}{%0.2f}"),("prob", "@{prob}{%0.2f}")]
                               , formatters={'price':'printf','prob':'printf'})
px_beta_dist_auto_fig = figure(plot_height=plot_config['height'], plot_width=plot_config['width'], title="Px Dist Plot - Auto",tools=[px_beta_dist_auto_hover])
px_beta_dist_auto_fig.line('price', 'prob', source=px_beta_dist_auto_source, color='steelblue', line_width=plot_config['line_width'], line_alpha=0.9)
px_beta_dist_auto_fig.circle('price', 'prob', source=px_beta_dist_auto_source, color='midnightblue', size=3, alpha=1)


# Set up the px_beta_dist_cust_fig
px_beta_dist_cust_df = QueryGUIData(data_config, ticker, 'px_beta_dist_cust')
px_beta_dist_cust_source = ColumnDataSource(data=dict(price=px_beta_dist_cust_df['price'], prob=px_beta_dist_cust_df['prob']))
px_beta_dist_cust_hover = HoverTool(tooltips=[("price", "$@{price}{%0.2f}"),("prob", "@{prob}{%0.2f}")]
                               , formatters={'price':'printf','prob':'printf'})
px_beta_dist_cust_fig = figure(plot_height=plot_config['height'], plot_width=plot_config['width'], title="Px Dist Plot",tools=[px_beta_dist_cust_hover])
px_beta_dist_cust_fig.line('price', 'prob', source=px_beta_dist_cust_source, color='steelblue', line_width=plot_config['line_width'], line_alpha=0.9)
px_beta_dist_cust_fig.circle('price', 'prob', source=px_beta_dist_cust_source, color='midnightblue', size=3, alpha=1)


# Set up widgets
ticker_input_fig = TextInput(title='Current Ticker: JNJ. Input a new ticker: ', value='JNJ')
px_beta_dist_cust_mode_input_fig = TextInput(title='Input the price that is most likely to achieve', value='e.g. 123.23')
px_beta_dist_cust_band_input_fig = TextInput(title='Input the difference between the max and min possible prices', value='e.g. 20.50')
px_beta_dist_cust_shape_input_fig = TextInput(title='Input the shape parameter (0 ~ 1), the smaller the flater', value='e.g. 0.5')
px_beta_dist_cust_skew_input_fig = TextInput(title='Input the skew parameter (-1 ~ 1), the smaller the more left', value='e.g. 0.4')
px_beta_dist_cust_update_button = Button(label='Click to confirm the input for the px_beta_dist_cust')

px_beta_dist_cust_conviction_input_fig = TextInput(title='Input the conviction of the ticker (1 ~ 10)', value='e.g. 7')
px_beta_dist_auto_update_button = Button(label='Click to update px_beta_dist_auto')
px_dist_normalize_button = Button(label='Using raw. Click to normalize px dist')


"""
offset = Slider(title="offset", value=0.0, start=-5.0, end=5.0, step=0.1)
amplitude = Slider(title="amplitude", value=1.0, start=-5.0, end=5.0, step=0.1)
phase = Slider(title="phase", value=0.0, start=0.0, end=2*np.pi)
freq = Slider(title="frequency", value=1.0, start=0.1, end=5.1, step=0.1)
"""

# Set up callbacks
def UpdateTickerOnChange(attrname, old, new):
    global ticker
    ticker = ticker_input_fig.value
    ticker_input_fig.title = 'Current Ticker: ' + ticker +'. Input a new ticker: '
    px_beta_dist_cust_conviction_input_fig.title = 'Input the conviction of the ticker (1-10)'
    
    px_series_results = QueryGUIData(data_config, ticker, 'px_series')
    px_series_df = px_series_results['df']
    volume_unit_str = px_series_results['volume_unit_str']
    px_series_source.data = dict(price=px_series_df['price'], volume=px_series_df['volume'], date=px_series_df['date'])
    px_series_fig.y_range.start=0.95*px_series_df['price'].min()
    px_series_fig.y_range.end=1.05*px_series_df['price'].max()
    px_series_fig.extra_y_ranges['volume'].start = 0
    px_series_fig.extra_y_ranges['volume'].end = 1.2*px_series_df['volume'].max()
    px_series_fig.yaxis[1].formatter = PrintfTickFormatter(format="%5.1f " + volume_unit_str)
    
    px_beta_dist_auto_df = QueryGUIData(data_config, ticker, 'px_beta_dist_autom')
    px_beta_dist_auto_source.data = dict(price=px_beta_dist_auto_df['price'], prob=px_beta_dist_auto_df['prob'])
    
    px_beta_dist_cust_df = QueryGUIData(data_config, ticker, 'px_beta_dist_cust')
    px_beta_dist_cust_source.data = dict(price=px_beta_dist_cust_df['price'], prob=px_beta_dist_cust_df['prob'])


#def UpdatePxBetaDistCustOnChange(attrname, old, new):
#    px_beta_dist_cust_input_fig.title = 'Value updated. Input additional "price prob" pairs, separate by ";"'
#    InsertPxBetaDist(data_config, ticker, px_beta_dist_cust_input_fig.value)
#    
#    px_beta_dist_cust_df = QueryGUIData(data_config, ticker, 'px_beta_dist_cust')
#    px_beta_dist_cust_source.data = dict(price=px_beta_dist_cust_df['price'], prob=px_beta_dist_cust_df['prob'])

def UpdatePxBetaDistCustOnChange():
    px_beta_dist_cust_update_button.label = 'Value updated. Click again after input new values.'
    para_dict = {'price_mode':px_beta_dist_cust_mode_input_fig.value,
                 'price_band':px_beta_dist_cust_band_input_fig.value,
                 'price_shape':px_beta_dist_cust_shape_input_fig.value,
                 'price_skew':px_beta_dist_cust_skew_input_fig.value}
    InsertPxBetaDist(data_config, ticker, 'cust', para_dict) #px_beta_dist_cust_input_fig.value
    
    px_beta_dist_cust_df = QueryGUIData(data_config, ticker, 'px_beta_dist_cust')
    px_beta_dist_cust_source.data = dict(price=px_beta_dist_cust_df['price'], prob=px_beta_dist_cust_df['prob'])


def UpdatePxBetaDistCustConvictionOnChange(attrname, old, new):
    value = px_beta_dist_cust_conviction_input_fig.value
    if CanToFloat(value) and float(value) >=1 and float(value)<=10:
        px_beta_dist_cust_conviction_input_fig.title = 'Updated. Input a new conviction of the ticker (1-10)'
        InsertPxDistConviction(data_config, ticker, 'Cust', value)
    else:
        px_beta_dist_cust_conviction_input_fig.title = 'Not Valid. Input a new conviction of the ticker (1-10)'


def UpdatePxBetaDistAutoOnChange():
    px_beta_dist_auto_update_button.label = 'Updated. Click again to update px_beta_dist_auto'
    InsertPxBetaDist(data_config, ticker)
    
    px_beta_dist_auto_df = QueryGUIData(data_config, ticker, 'px_beta_dist_autol') ###TODO: to be changed to switch between distributions
    px_beta_dist_auto_source.data = dict(price=px_beta_dist_auto_df['price'], prob=px_beta_dist_auto_df['prob'])

def NormalizePxBetaDistOnChange():
    if px_dist_normalize_button.label == 'Using raw. Click to normalize px dist':
        px_dist_normalize_button.label = 'Normalized. Click again to use raw px dist'
        
        #px_beta_dist_auto_df = QueryGUIData(data_config, ticker, 'px_beta_dist_autom', True)
        #px_beta_dist_auto_source.data = dict(price=px_beta_dist_auto_df['price'], prob=px_beta_dist_auto_df['prob'])
        
        px_beta_dist_cust_df = QueryGUIData(data_config, ticker, 'px_beta_dist_cust', True)
        px_beta_dist_cust_source.data = dict(price=px_beta_dist_cust_df['price'], prob=px_beta_dist_cust_df['prob'])
    elif px_dist_normalize_button.label == 'Normalized. Click again to use raw px dist':
        px_dist_normalize_button.label = 'Using raw. Click to normalize px dist'
        
        #px_beta_dist_auto_df = QueryGUIData(data_config, ticker, 'px_beta_dist_autom', False)
        #px_beta_dist_auto_source.data = dict(price=px_beta_dist_auto_df['price'], prob=px_beta_dist_auto_df['prob'])
        
        px_beta_dist_cust_df = QueryGUIData(data_config, ticker, 'px_beta_dist_cust', False)
        px_beta_dist_cust_source.data = dict(price=px_beta_dist_cust_df['price'], prob=px_beta_dist_cust_df['prob'])
    else:
        px_dist_normalize_button.label = 'Unexpected px_dist_normalize_button.label! Contact support.'


"""
def PrintUponChange(attrname, old, new):
    # Get the current slider values
    a = amplitude.value
    b = offset.value
    w = phase.value
    k = freq.value
    print(a,b,w,k)


for w in [offset, amplitude, phase, freq]:
    w.on_change('value', PrintUponChange)
"""

# update
#px_beta_dist_cust_input_fig.on_change('value', UpdatePxBetaDistCustOnChange)
px_beta_dist_cust_update_button.on_click(UpdatePxBetaDistCustOnChange)
px_beta_dist_cust_conviction_input_fig.on_change('value', UpdatePxBetaDistCustConvictionOnChange)
ticker_input_fig.on_change('value', UpdateTickerOnChange)
px_beta_dist_auto_update_button.on_click(UpdatePxBetaDistAutoOnChange)
px_dist_normalize_button.on_click(NormalizePxBetaDistOnChange)



# Set up layouts and add to document
#interactions = widgetbox(text, offset, amplitude, phase, freq)
interactions = widgetbox(ticker_input_fig
                         , px_beta_dist_cust_mode_input_fig
                         , px_beta_dist_cust_band_input_fig
                         , px_beta_dist_cust_shape_input_fig
                         , px_beta_dist_cust_skew_input_fig
                         , px_beta_dist_cust_update_button
                         , px_beta_dist_cust_conviction_input_fig
                         , px_beta_dist_auto_update_button
                         , px_dist_normalize_button)

curdoc().add_root(gridplot([ [desc]
                           ,[interactions, px_beta_dist_cust_fig, px_beta_dist_auto_fig]
                           ,[px_series_fig, None, None]
                          ]))

#curdoc().add_root(row(inputs, px_beta_dist_cust_fig, width=800))
curdoc().title = "DQ Project - Graphic User Interface"


