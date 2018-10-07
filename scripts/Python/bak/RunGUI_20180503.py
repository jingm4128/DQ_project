# -*- coding: utf-8 -*-
"""
Created on Mon Apr  2 00:58:47 2018

@author: IBM
"""

#import bokeh
from bokeh.plotting import figure, output_file, show
from bokeh.layouts import gridplot, widgetbox, row
from bokeh.models import Range1d, LinearAxis, PrintfTickFormatter, CustomJS, TextInput, Paragraph, ColumnDataSource
from bokeh.models.widgets import TextInput, Slider
from bokeh.io import curdoc
#from bokeh.models.widgets import Slider

import pandas
import numpy as np

from ExecQuery import ExecQuery
from config import RunGUI_config
data_config = RunGUI_config['data']
plot_config = RunGUI_config['plot']
ticker = 'JNJ'
print('test')

def main():
    print('test')
    #PlotAll(plot_config, data_config, ticker)
    InteractivePlot(plot_config, data_config, ticker)

#########################################
### The Function
#########################################
def PlotAll(plot_config, data_config, ticker):
    output_dir = plot_config['output_dir'] 
    
    
    px_series_df = QueryData(data_config, ticker, 'px_series')
    #px_series_df_curr = px_series_df[px_series_df['date']==px_series_df['date'].max()]
    px_dist_crude_df = QueryData(data_config, ticker, 'px_dist_crude')
    px_dist_manual_df = QueryData(data_config, ticker, 'px_dist_manual')
    
    #1. the first plot - price and volume time series
    px_series_fig = PlotTickerPriceVolume(plot_config, px_series_df)
    #show(px_series_fig)
    
    #2. price and prob based on the crude model
    px_dist_crude_fig = PlotPdf(plot_config, px_dist_crude_df, 'crude')
    #show(px_dist_crude_fig)

    #3. price and prob based on the manual model
    px_dist_manual_fig = PlotPdf(plot_config, px_dist_manual_df, 'manual')
    #show(px_dist_manual_fig)
    
    #4. the input box
    input_box_fig = PlotInputBox(plot_config)
    #show(input_box_fig)
    
    p = gridplot([[px_series_fig, input_box_fig, None]
                , [px_dist_crude_fig, px_dist_manual_fig, None]])
    output_file(output_dir+"px_dist.html", title="px_dist")
    show(p)



    

#########################################
### The Secondary Plot Functions
#########################################
def PlotTickerPriceVolume(plot_config, px_series_df):
    plot_options = dict(width=2*plot_config['width'], plot_height=plot_config['height'], tools=plot_config['tools'])
    
    vol_unit = 1e6 if px_series_df['volume'].max()>1e6 else 1e3
    px_series_df['volume_norm'] = px_series_df['volume']/vol_unit
    
    px_series_fig = figure(**plot_options, x_axis_type="datetime", title = "px_series")
    px_series_fig.y_range = Range1d(start=0.95*px_series_df['price'].min(), end=1.05*px_series_df['price'].max())
    
    px_series_fig.extra_y_ranges = {"volume": Range1d(start=0, end=1.2*px_series_df['volume_norm'].max())}
    px_series_fig.add_layout(LinearAxis(y_range_name='volume'), 'right')
    px_series_fig.yaxis[1].formatter = PrintfTickFormatter(format="%5.1f " + 'M' if vol_unit==1e6 else 'K')
    
    px_series_fig.line(px_series_df['date'], px_series_df['price'], line_width=2, color='navy', alpha=0.5)
    px_series_fig.vbar(bottom=0, top=px_series_df['volume_norm'], x=px_series_df['date'], width=0.9, color='grey', alpha=0.2, y_range_name='volume')
    
    return px_series_fig


def PlotPdf(plot_config, px_dist_df, dist_type='crude'):
    plot_options = dict(width=plot_config['width'], plot_height=plot_config['height'], tools=plot_config['tools'])
    
    px_dist_fig = figure(**plot_options, title = "px_dist - " + dist_type)
    px_dist_fig.line(px_dist_df['price'], px_dist_df['prob'], line_width=2, color='navy', alpha=0.5)
    
    #show(px_dist_fig)
    return px_dist_fig


def PlotInputBox(plot_config):
    plot_options = dict(width=plot_config['width'], height=plot_config['height'])
    output_msg = 'You have entered:'
    
    # TAKE ONLY OUTPUT
    text_input_box = Paragraph(text=output_msg, **plot_options)
    
    # CALLBACKS
    def callback_print(text_input_box=text_input_box):
        user_input = str(cb_obj.value)
        output_msg = 'You have entered: ' + user_input
        text_input_box.text = output_msg
    
    # USER INTERACTIONS
    text_input = TextInput(value="", title="Enter the text:"
                           , callback=CustomJS.from_py_func(callback_print))

    widg = widgetbox(text_input, text_input_box)
    
    return widg

def InteractivePlot(plot_config, data_config, ticker):
    plot_options = dict(width=plot_config['width'], height=plot_config['height'], tools=plot_config['tools'])
    
    px_dist_df = QueryData(data_config, ticker, 'px_dist_manual')
    source = ColumnDataSource(data=dict(x=px_dist_df['price'], y=px_dist_df['prob']))
    
    # Set up plot
    plot = figure(**plot_options)
    plot.line('price', 'prob', source=source, line_width=2, line_alpha=0.5)
    text = TextInput(title='Please input the "price prob" pairs, separated by ";"', value='e.g. 123.23 0.2')
    
    # Set up callbacks
    def update_title(attrname, old, new):
        plot.title.text = 'Value updated, please input additional "price prob" pairs, separated by ";"'
    
    def update_data(attrname, old, new):
        InsertPXDistManual(data_config, ticker, text.value)
        px_dist_df = QueryData(data_config, ticker, 'px_dist_manual')
        source.data = dict(x=px_dist_df['price'], y=px_dist_df['prob'])
    
    text.on_change('value', update_title)
    text.on_change('value', update_data)    
    
    # Set up layouts and add to document
    inputs = widgetbox(text)
    
    curdoc().add_root(row(inputs, plot))
    curdoc().title = "InputBox"
    
    show(inputs)




#########################################
### The Secondary Query Functions
#########################################
def QueryData(data_config, ticker, data_type):
    db = data_config['database']
      
    if data_type == 'px_series':
        px_series_table = data_config['px_series_table']
        px_series_query = """select date, adj_close as price, volume 
                             from """+px_series_table+""" 
                             where ticker = '"""+ticker+"""' 
                             order by ticker, date;"""
        print(px_series_query)
        px_series_df = ExecQuery(db, px_series_query, True, True)
        return px_series_df
    
    elif data_type == 'px_dist_crude':
        px_dist_table = data_config['px_dist_table']
        
        max_dt_subquery = """(
                                select ticker, price, max(asof_datetime) as max_dt
                                from """+px_dist_table+""" 
                                where ticker='"""+ticker+"""' 
                                and model='crude' 
                                group by 1,2
                             )"""
        px_dist_query = """ select p.price, p.prob, conviction
                            from """+px_dist_table+""" p
                            join """+max_dt_subquery+""" s 
                            on p.price=s.price and p.asof_datetime=s.max_dt #and p.ticker=s.ticker
                            where p.ticker='"""+ticker+"""' 
                            and p.model='crude'
                            order by price
                         ;"""
        print(px_dist_query)
        px_dist_crude_df = ExecQuery(db, px_dist_query, True, True)
        px_dist_crude_df['prob'] = px_dist_crude_df['prob']/px_dist_crude_df['prob'].sum()
        return px_dist_crude_df
    
    elif data_type == 'px_dist_manual':
        px_dist_table = data_config['px_dist_table']
        
        max_dt_subquery = """(
                                select ticker, price, max(asof_datetime) as max_dt
                                from """+px_dist_table+""" 
                                where ticker='"""+ticker+"""' 
                                and model='manual' 
                                group by 1,2
                             )"""
        px_dist_query = """ select p.price, p.prob, conviction
                            from """+px_dist_table+""" p
                            join """+max_dt_subquery+""" s 
                            on p.price=s.price and p.asof_datetime=s.max_dt #and p.ticker=s.ticker
                            where p.ticker='"""+ticker+"""' 
                            and p.model='manual'
                            order by price
                         ;"""
        print(px_dist_query)
        px_dist_manual_df = ExecQuery(db, px_dist_query, True, True)
        px_dist_manual_df['prob'] = px_dist_manual_df['prob']/px_dist_manual_df['prob'].sum()
        return px_dist_manual_df
    

def InsertPXDistManual(data_config, ticker, raw_str):
    """
        the input should look like "123.12 0.1;123.23 0.15" 
        - if duplicated, will take the latter one
        - if not able to convert to float, will skip
    """
    raw_str = "123.12 0.1;123.23 0.15;123.12 0.3;123df 0.2" ###DEBUG
    ticker = 'JNJ' ###DEBUG
    
    # 1. process the string
    #px_dist_dict = {StrToFloat(x.split(' ')[0]):StrToFloat(x.split(' ')[1]) for x in raw_str.split(';')}
    px_dist_dict = {x.split(' ')[0]:x.split(' ')[1] for x in raw_str.split(';') if CanToFloat(x.split(' ')[0]) and CanToFloat(x.split(' ')[1])}
    
    # 2. condtruct the query
    query_list = []
    query_prepend = ', '.join(['current_timestamp() as datetime',"'manual' as model", "'"+ticker+"' as ticker"])
    
    for i in px_dist_dict.keys():
        query_list.append('(select ' +str(i)+' as price, '+str(px_dist_dict[i])+' as prob)')
    
    select_query = 'select '+query_prepend+', temp.*, null as conviction from (\n'+ '\nUNION ALL\n'.join(query_list) +'\n) as temp'
    insert_query = 'insert into '+data_config['px_dist_table']+' \n'+ select_query + '; commit;'
    print(insert_query)
    ExecQuery(data_config['database'], insert_query, False, False)        


def InsertPxDistCrude(data_config, ticker):
    
    query_list = []
    px_dist_dict = {'0':'0.2',
                    '0.1':'0.1','-0.1':'0.1',
                    '0.2':'0.08','-0.2':'0.08',
                    '0.3':'0.06','-0.3':'0.06',
                    '0.5':'0.05','-0.5':'0.05',
                    '1':'0.04','-1':'0.04',
                    '2':'0.03','-2':'0.03'
                   }
    for i in px_dist_dict.keys():
        query_list.append('(select avg(adj_close)+('+i+'*stddev(adj_close)) as price, '+px_dist_dict[i]+' from '+data_config['px_series_table']+" where ticker='"+ticker+"')")
    
    
    insert_query = """insert into """ +data_config['px_dist_table']+ """
                    select current_timestamp() as datetime, 'crude' as model, '"""+ticker+"""' as ticker, temp.*, 1 as conviction
                    from
                    (\n""" + '\nUNION ALL\n'.join(query_list) + """\n) as temp
                    ; commit;
                   """
    print(insert_query)
    ExecQuery(data_config['database'], insert_query, False, False)    


#########################################
### The Tertiary Helper Functions
#########################################
def StrToFloat(str):
    try:
        f = float(str)
    except ValueError:
        f = None
    return f
        
def CanToFloat(str):
    try:
        float(str)
        return True
    except ValueError:
        return False
        


#########################################
### Execute
#########################################
        """
if __name__ == '__main__':
    main()
    """

plot_options = dict(width=plot_config['width'], height=plot_config['height'], tools=plot_config['tools'])

px_dist_df = QueryData(data_config, ticker, 'px_dist_manual')
source = ColumnDataSource(data=dict(x=px_dist_df['price'], y=px_dist_df['prob']))

# Set up plot
plot = figure(**plot_options)
plot.line('price', 'prob', source=source, line_width=2, line_alpha=0.5)
text = TextInput(title='Please input the "price prob" pairs, separated by ";"', value='e.g. 123.23 0.2')

# Set up callbacks
def update_title(attrname, old, new):
    plot.title.text = 'Value updated, please input additional "price prob" pairs, separated by ";"'

def update_data(attrname, old, new):
    InsertPXDistManual(data_config, ticker, text.value)
    px_dist_df = QueryData(data_config, ticker, 'px_dist_manual')
    source.data = dict(x=px_dist_df['price'], y=px_dist_df['prob'])

text.on_change('value', update_title)
text.on_change('value', update_data)    

# Set up layouts and add to document
inputs = widgetbox(text)

curdoc().add_root(row(inputs, plot), width=2*plot_config['width'], height=2*plot_config['height'])
curdoc().title = "InputBox"

show(inputs)