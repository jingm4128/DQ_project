# -*- coding: utf-8 -*-
"""
Created on Mon Apr  2 00:58:47 2018
Last modified on 20181007 - added comments

@author: Jing Ma

    bokeh serve E:\Work\PartTime\DQ_project\scripts\Python\RunGUI_no_dist.py
at your command prompt. Then navigate to the URL
    http://localhost:5006/RunGUI_no_dist.py
in your browser.

This version does not do any interpolation, but would plot
1) the (price, probability) pair that you put in
2) the crude distribution (manually made up)
3) the market price_volume data

Note that ***no distribution is assumed***, later interpolation might be needed for optimization
"""


import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import gridplot, widgetbox
from bokeh.models import Range1d, LinearAxis, ColumnDataSource, PrintfTickFormatter, DatetimeTickFormatter, HoverTool, Div
from bokeh.models.widgets import Slider, TextInput, Button
from bokeh.plotting import figure
from os.path import dirname, join



from RunGUI_help import CanToFloat, QueryGUIData, InsertPXDistManual, InsertPxDistCrude, InsertPxDistConviction
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


# Set up the px_dist_crude_fig
px_dist_crude_df = QueryGUIData(data_config, ticker, 'px_dist_crude')
px_dist_crude_source = ColumnDataSource(data=dict(price=px_dist_crude_df['price'], prob=px_dist_crude_df['prob']))
px_dist_crude_hover = HoverTool(tooltips=[("price", "$@{price}{%0.2f}"),("prob", "@{prob}{%0.2f}")]
                               , formatters={'price':'printf','prob':'printf'})
px_dist_crude_fig = figure(plot_height=plot_config['height'], plot_width=plot_config['width'], title="Px Dist Plot - Crude",tools=[px_dist_crude_hover])
px_dist_crude_fig.line('price', 'prob', source=px_dist_crude_source, color='steelblue', line_width=plot_config['line_width'], line_alpha=0.9)
px_dist_crude_fig.circle('price', 'prob', source=px_dist_crude_source, color='midnightblue', size=3, alpha=1)


# Set up the px_dist_manual_fig
px_dist_manual_df = QueryGUIData(data_config, ticker, 'px_dist_manual')
px_dist_manual_source = ColumnDataSource(data=dict(price=px_dist_manual_df['price'], prob=px_dist_manual_df['prob']))
px_dist_manual_hover = HoverTool(tooltips=[("price", "$@{price}{%0.2f}"),("prob", "@{prob}{%0.2f}")]
                               , formatters={'price':'printf','prob':'printf'})
px_dist_manual_fig = figure(plot_height=plot_config['height'], plot_width=plot_config['width'], title="Px Dist Plot",tools=[px_dist_manual_hover])
px_dist_manual_fig.line('price', 'prob', source=px_dist_manual_source, color='steelblue', line_width=plot_config['line_width'], line_alpha=0.9)
px_dist_manual_fig.circle('price', 'prob', source=px_dist_manual_source, color='midnightblue', size=3, alpha=1)


# Set up widgets
ticker_input_fig = TextInput(title='Current Ticker: JNJ. Input a new ticker: ', value='JNJ')
px_dist_manual_input_fig = TextInput(title='Input the "price prob" pairs, separate by ";"', value='e.g. 123.23 0.2')
px_dist_manual_conviction_input_fig = TextInput(title='Input the conviction of the ticker (1-10)', value='e.g. 7')
px_dist_crude_update_button = Button(label='Click to update px_dist_crude')
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
    px_dist_manual_conviction_input_fig.title = 'Input the conviction of the ticker (1-10)'
    
    px_series_results = QueryGUIData(data_config, ticker, 'px_series')
    px_series_df = px_series_results['df']
    volume_unit_str = px_series_results['volume_unit_str']
    px_series_source.data = dict(price=px_series_df['price'], volume=px_series_df['volume'], date=px_series_df['date'])
    px_series_fig.y_range.start=0.95*px_series_df['price'].min()
    px_series_fig.y_range.end=1.05*px_series_df['price'].max()
    px_series_fig.extra_y_ranges['volume'].start = 0
    px_series_fig.extra_y_ranges['volume'].end = 1.2*px_series_df['volume'].max()
    px_series_fig.yaxis[1].formatter = PrintfTickFormatter(format="%5.1f " + volume_unit_str)
    
    px_dist_crude_df = QueryGUIData(data_config, ticker, 'px_dist_crude')
    px_dist_crude_source.data = dict(price=px_dist_crude_df['price'], prob=px_dist_crude_df['prob'])
    
    px_dist_manual_df = QueryGUIData(data_config, ticker, 'px_dist_manual')
    px_dist_manual_source.data = dict(price=px_dist_manual_df['price'], prob=px_dist_manual_df['prob'])


def UpdatePxDistManualOnChange(attrname, old, new):
    px_dist_manual_input_fig.title = 'Value updated. Input additional "price prob" pairs, separate by ";"'
    InsertPXDistManual(data_config, ticker, px_dist_manual_input_fig.value)
    
    px_dist_manual_df = QueryGUIData(data_config, ticker, 'px_dist_manual')
    px_dist_manual_source.data = dict(price=px_dist_manual_df['price'], prob=px_dist_manual_df['prob'])


def UpdatePxDistManualConvictionOnChange(attrname, old, new):
    px_dist_manual_conviction_input_fig.title = 'Updated. Input a new conviction of the ticker (1-10)'
    if CanToFloat(px_dist_manual_conviction_input_fig.value):
        InsertPxDistConviction(data_config, ticker, 'manual', px_dist_manual_conviction_input_fig.value)
    else:
        px_dist_manual_conviction_input_fig.title = 'Not Valid. Input a new conviction of the ticker (1-10)'


def UpdatePxDistCrudeOnChange():
    px_dist_crude_update_button.label = 'Updated. Click again to update px_dist_crude'
    InsertPxDistCrude(data_config, ticker)
    
    px_dist_crude_df = QueryGUIData(data_config, ticker, 'px_dist_crude')
    px_dist_crude_source.data = dict(price=px_dist_crude_df['price'], prob=px_dist_crude_df['prob'])

def NormalizePxDistOnChange():
    if px_dist_normalize_button.label == 'Using raw. Click to normalize px dist':
        px_dist_normalize_button.label = 'Normalized. Click again to use raw px dist'
        
        px_dist_crude_df = QueryGUIData(data_config, ticker, 'px_dist_crude', True)
        px_dist_crude_source.data = dict(price=px_dist_crude_df['price'], prob=px_dist_crude_df['prob'])
        
        px_dist_manual_df = QueryGUIData(data_config, ticker, 'px_dist_manual', True)
        px_dist_manual_source.data = dict(price=px_dist_manual_df['price'], prob=px_dist_manual_df['prob'])
    elif px_dist_normalize_button.label == 'Normalized. Click again to use raw px dist':
        px_dist_normalize_button.label = 'Using raw. Click to normalize px dist'
        
        px_dist_crude_df = QueryGUIData(data_config, ticker, 'px_dist_crude', False)
        px_dist_crude_source.data = dict(price=px_dist_crude_df['price'], prob=px_dist_crude_df['prob'])
        
        px_dist_manual_df = QueryGUIData(data_config, ticker, 'px_dist_manual', False)
        px_dist_manual_source.data = dict(price=px_dist_manual_df['price'], prob=px_dist_manual_df['prob'])
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
px_dist_manual_input_fig.on_change('value', UpdatePxDistManualOnChange)
px_dist_manual_conviction_input_fig.on_change('value', UpdatePxDistManualConvictionOnChange)
ticker_input_fig.on_change('value', UpdateTickerOnChange)
px_dist_crude_update_button.on_click(UpdatePxDistCrudeOnChange)
px_dist_normalize_button.on_click(NormalizePxDistOnChange)



# Set up layouts and add to document
#interactions = widgetbox(text, offset, amplitude, phase, freq)
interactions = widgetbox(ticker_input_fig, px_dist_manual_input_fig, px_dist_manual_conviction_input_fig
                         , px_dist_crude_update_button, px_dist_normalize_button)

curdoc().add_root(gridplot([ [desc]
                           ,[interactions, px_dist_manual_fig, px_dist_crude_fig]
                           ,[px_series_fig, None, None]
                          ]))

#curdoc().add_root(row(inputs, px_dist_manual_fig, width=800))
curdoc().title = "DQ Project - Graphic User Interface"


