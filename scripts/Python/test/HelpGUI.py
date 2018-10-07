# -*- coding: utf-8 -*-
"""
Created on Mon Apr  2 00:58:47 2018

@author: IBM
"""

#import bokeh
from bokeh.plotting import figure, output_file, show
from bokeh.layouts import gridplot
from bokeh.models import Range1d, LinearAxis, PrintfTickFormatter, ColumnDataSource
#from bokeh.models.widgets import Slider

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


from ExecQuery import ExecQuery
from config import RunGUI_config
data_config = RunGUI_config['data']
plot_config = RunGUI_config['plot']
#ticker = 'JNJ'

def main():
    PlotAll(plot_config, data_config, 'JNJ')

#########################################
### The Function
#########################################
def PlotAll(plot_config, data_config, ticker):
    output_dir = plot_config['output_dir'] 
    
    
    px_series_df = QueryGUIData(data_config, ticker, 'px_series')
    #px_series_df_curr = px_series_df[px_series_df['date']==px_series_df['date'].max()]
    px_dist_crude_df = QueryGUIData(data_config, ticker, 'px_dist_crude')
    px_dist_manual_df = QueryGUIData(data_config, ticker, 'px_dist_manual')
    
    #1. the first plot - price and volume time series
    px_series_fig = PlotPriceVolume(plot_config, px_series_df)
    #show(px_series_fig)
    
    #2. price and prob based on the crude model
    px_dist_crude_fig = PlotPdf(plot_config, px_dist_crude_df, 'crude')
    #show(px_dist_crude_fig)

    #3. price and prob based on the manual model
    px_dist_manual_fig = PlotPdf(plot_config, px_dist_manual_df, 'manual')
    #show(px_dist_manual_fig)
    
    
    p = gridplot([[px_series_fig, None]
                , [px_dist_crude_fig, px_dist_manual_fig]])
    output_file(output_dir+"px_dist.html", title="px_dist")
    show(p)



    
#########################################
### The Secondary Plot Functions
#########################################
def PlotPriceVolume(plot_config, px_series_results):
    px_series_df = px_series_results['df']
    volume_unit_str = px_series_results['volume_unit_str']
    px_series_source = ColumnDataSource(data=dict(price=px_series_df['price'], volume=px_series_df['volume'], date=px_series_df['date']))
    #type(px_series_source.data['volume'])
    
    plot_options = dict(width=int(2.5*plot_config['width']), plot_height=plot_config['height'], tools=plot_config['tools'])
    px_series_fig = figure(**plot_options, x_axis_type="datetime", title = "Price Volume Time Series")
    px_series_fig.y_range = Range1d(start=0.95*px_series_df['price'].min(), end=1.05*px_series_df['price'].max())
    px_series_fig.extra_y_ranges = {"volume": Range1d(start=0, end=1.2*px_series_df['volume'].max())}
    print(px_series_df['volume'], px_series_df['volume'].max())
    px_series_fig.add_layout(LinearAxis(y_range_name='volume'), 'right')
    px_series_fig.yaxis[1].formatter = PrintfTickFormatter(format="%5.1f " + volume_unit_str)
    
    px_series_fig.line('date', 'price', source=px_series_source, line_width=plot_config['line_width'], color='olivedrab', alpha=0.9)
    px_series_fig.vbar(bottom=0, top='volume', x='date', source=px_series_source, width=1.5, color='grey', alpha=0.5, y_range_name='volume')
    
    return px_series_fig


def PlotPdf(plot_config, px_dist_df, dist_type='Crude'):
    plot_options = dict(width=plot_config['width'], plot_height=plot_config['height'], tools=plot_config['tools'])
    
    px_dist_fig = figure(**plot_options, title = "Px Dist Plot - " + dist_type)
    px_dist_fig.line(px_dist_df['price'], px_dist_df['prob'], line_width=plot_config['line_width'], color='steelblue', alpha=0.9)
    
    #show(px_dist_fig)
    return px_dist_fig





#########################################
### The Secondary Query Functions
#########################################
def QueryGUIData(data_config, ticker, data_type, normalize=False):
    db = data_config['database']
      
    if data_type == 'px_series':
        px_series_table = data_config['px_series_table']
        px_series_query = """select date as date_raw, adj_close as price, volume as volume_raw 
                             from """+px_series_table+""" 
                             where ticker = '"""+ticker+"""' 
                             order by ticker, date;"""
        print(px_series_query)
        px_series_df = ExecQuery(db, px_series_query, True, True)
        
        px_series_df['date'] = pd.to_datetime(px_series_df['date_raw'], format='%Y-%m-%d') + timedelta(hours=16)
        
        volume_unit = 1e6 if px_series_df['volume_raw'].max()>1e6 else 1e3
        px_series_df['volume'] = px_series_df['volume_raw']/volume_unit
        volume_unit_str = 'M' if volume_unit==1e6 else 'K'

        return {'df':px_series_df[['date','price','volume']], 'volume_unit_str':volume_unit_str}
    
    elif data_type == 'px_dist_crude':
        px_dist_table = data_config['px_dist_table']
        
        max_dt_subquery = """(
                                select ticker, price, max(asof_datetime) as max_dt
                                from """+px_dist_table+""" 
                                where ticker='"""+ticker+"""' 
                                and model='crude'
                                and not deprecated
                                group by 1,2
                             )"""
        px_dist_query = """ select p.price, p.prob
                            from """+px_dist_table+""" p
                            join """+max_dt_subquery+""" s 
                            on p.price=s.price and p.asof_datetime=s.max_dt #and p.ticker=s.ticker
                            where p.ticker='"""+ticker+"""' 
                            and p.model='crude'
                            and not deprecated
                            order by price
                         ;"""
        print(px_dist_query)
        px_dist_crude_df = ExecQuery(db, px_dist_query, True, True)
        if normalize:
            px_dist_crude_df['prob'] = px_dist_crude_df['prob']/px_dist_crude_df['prob'].sum()
        return px_dist_crude_df
    
    elif data_type == 'px_dist_manual':
        px_dist_table = data_config['px_dist_table']
        
        max_dt_subquery = """(
                                select ticker, price, max(asof_datetime) as max_dt
                                from """+px_dist_table+""" 
                                where ticker='"""+ticker+"""' 
                                and model='manual'
                                and not deprecated
                                group by 1,2
                             )"""
        px_dist_query = """ select p.price, p.prob
                            from """+px_dist_table+""" p
                            join """+max_dt_subquery+""" s 
                            on p.price=s.price and p.asof_datetime=s.max_dt #and p.ticker=s.ticker
                            where p.ticker='"""+ticker+"""' 
                            and p.model='manual'
                            and not deprecated
                            order by price
                         ;"""
        print(px_dist_query)
        px_dist_manual_df = ExecQuery(db, px_dist_query, True, True)
        if normalize:
            px_dist_manual_df['prob'] = px_dist_manual_df['prob']/px_dist_manual_df['prob'].sum()
        return px_dist_manual_df
    

def InsertPXDistManual(data_config, ticker, raw_str):
    """
        the input should look like "123.12 0.1;123.23 0.15" 
        - if duplicated, will take the latter one
        - if not able to convert to float, will skip
    """
    #raw_str = "123.12 0.1;123.23 0.15;123.12 0.3;123df 0.2" ###DEBUG
    #ticker = 'JNJ' ###DEBUG
    
    # 1. process the string
    # 1.1 if the string is "clear all", mark everything for this ticker to be deprecated
    if raw_str == 'clear all':
        deprecate_query = 'update '+data_config['px_dist_table']+" set deprecated=True where ticker = '"+ticker+"' and model = 'manual'; commit;"
        print(deprecate_query)
        ExecQuery(data_config['database'], deprecate_query, False, False)
    
    # 1.2 subtract numbers, and proceed if there is any ligit numbers
    px_dist_dict = {x.split(' ')[0]:x.split(' ')[1] for x in raw_str.split(';') if CanToFloat(x.split(' ')[0]) and CanToFloat(x.split(' ')[1])}
    if len(px_dist_dict)==0: return None
    
    # 2. construct the query
    query_list = []
    query_prepend = ', '.join(['current_timestamp() as asof_datetime',"'manual' as model", "'"+ticker+"' as ticker"])
    
    for i in px_dist_dict.keys():
        query_list.append('(select ' +str(i)+' as price, '+str(px_dist_dict[i])+' as prob)')
    
    select_query = 'select '+query_prepend+', temp.*, false as deprecated from (\n'+ '\nUNION ALL\n'.join(query_list) +'\n) as temp'
    insert_query = 'insert into '+data_config['px_dist_table']+' \n'+ select_query + '; commit;'
    
    print(insert_query)
    ExecQuery(data_config['database'], insert_query, False, False)


def InsertPxDistCrude(data_config, ticker):
    
    deprecate_query = 'update '+data_config['px_dist_table']+" set deprecated=True where ticker = '"+ticker+"' and model = 'crude'; commit;"
    print(deprecate_query)
    ExecQuery(data_config['database'], deprecate_query, False, False)
    
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
        query_list.append('(select avg(adj_close)+('+i+'*stddev(adj_close)) as price, '+px_dist_dict[i]+' as prob from '+data_config['px_series_table']+" where ticker='"+ticker+"')")
    
    
    insert_query = """insert into """ +data_config['px_dist_table']+ """
                    select current_timestamp() as asof_datetime, 'crude' as model, '"""+ticker+"""' as ticker, temp.*, false as deprecated
                    from
                    (\n""" + '\nUNION ALL\n'.join(query_list) + """\n) as temp
                    ; commit;
                   """
    print(insert_query)
    ExecQuery(data_config['database'], insert_query, False, False)    


def InsertPxDistConviction(data_config, ticker, model, conviction):
    # conviction should be a string that can be translated into float
    insert_query = """insert into """ +data_config['px_dist_conviction_table']+ """
                      select current_timestamp() as asof_datetime, 
                           '"""+model+"""' as model, 
                           '"""+ticker+"""' as ticker, 
                           """+conviction+"""as conviction, 
                           false as deprecated; commit;
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
if __name__ == '__main__':
    main()
