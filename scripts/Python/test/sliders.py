''' Present an interactive function explorer with slider widgets.
Scrub the sliders to change the properties of the ``sin`` curve, or
type into the title text box to update the title of the plot.
Use the ``bokeh serve`` command to run the example by executing:
    bokeh serve sliders.py
at your command prompt. Then navigate to the URL
    http://localhost:5006/sliders
in your browser.
'''
import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Slider, TextInput
from bokeh.plotting import figure




from ExecQuery import ExecQuery
from config import RunGUI_config
data_config = RunGUI_config['data']
plot_config = RunGUI_config['plot']


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


# Set up data
ticker = 'JNJ'
px_dist_df = QueryData(data_config, ticker, 'px_dist_manual')
source = ColumnDataSource(data=dict(x=px_dist_df['price'], y=px_dist_df['prob']))
    


# Set up plot
plot = figure(plot_height=400, plot_width=400, title="my sine wave",
              tools="crosshair,pan,reset,save,wheel_zoom",
              x_range=[0, 200], y_range=[0, 1])

plot.line('x', 'y', source=source, line_width=3, line_alpha=0.6)


# Set up widgets
text = TextInput(title="title", value='my sine wave')
offset = Slider(title="offset", value=0.0, start=-5.0, end=5.0, step=0.1)
amplitude = Slider(title="amplitude", value=1.0, start=-5.0, end=5.0, step=0.1)
phase = Slider(title="phase", value=0.0, start=0.0, end=2*np.pi)
freq = Slider(title="frequency", value=1.0, start=0.1, end=5.1, step=0.1)


# Set up callbacks

def print_title():
    text_file = open("Output.txt", "w")
    text_file.write(text.value + '\n')
    text_file.close()

def update_title(attrname, old, new):
    plot.title.text = text.value
    print_title()


def CanToFloat(str):
    try:
        float(str)
        return True
    except ValueError:
        return False

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

text.on_change('value', update_title)

def update_data(attrname, old, new):

    # Get the current slider values
    a = amplitude.value
    b = offset.value
    w = phase.value
    k = freq.value

    # Generate the new curve
    InsertPXDistManual(data_config, ticker, text.value)
    px_dist_df = QueryData(data_config, ticker, 'px_dist_manual')
    source.data = dict(x=px_dist_df['price'], y=px_dist_df['prob'])

for w in [offset, amplitude, phase, freq]:
    w.on_change('value', update_data)


# Set up layouts and add to document
inputs = widgetbox(text, offset, amplitude, phase, freq)

curdoc().add_root(row(inputs, plot, width=800))
curdoc().title = "Sliders"


