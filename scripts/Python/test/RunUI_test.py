# -*- coding: utf-8 -*-
"""
Created on Mon Apr  2 00:58:47 2018

@author: IBM
"""

import pandas as pd
#from ExecQuery import ExecQuery
from GetPxData import DumpDfDataFromQuandl

"""
### interfaces
bokeh.model #developing apps
bokeh.plotting #higher level with some customizaions
"""

from bokeh.plotting import figure, output_file, show
from bokeh.models.annotations import Title
from bokeh.layouts import widgetbox
from bokeh.models.widgets import Slider


### create the data set
df_AAPL = DumpDfDataFromQuandl('2018-01-01', '2018-02-20', 'AAPL')
df_SIRI = DumpDfDataFromQuandl('2018-01-01', '2018-02-20', 'SIRI')
df = pd.merge(df_AAPL, df_SIRI, on='date', how='inner', suffixes=('_AAPL', '_SIRI'))


### create the figure
# fot tools, tools='' is the same as not specifying, and  you can select form the list
# if sizing_mode is set to 'scale_width', the graph size will adjust for the browser window size; and otherwise when set to 'fixed'
# x_axis_type='datetime'
#p = figure(plot_width=500, plot_height=400, title='temp_title', tools='pan, box_select, box_zoom, wheel_zoom, reset, save', logo=None)
p = figure(plot_width=560, plot_height=420, title='temp_title', tools='pan, wheel_zoom, reset, save', logo=None, x_axis_type='datetime', sizing_mode='fixed')
#p = figure(plot_width=500, plot_height=400, title='temp_title', tools='')
#p = figure(plot_width=500, plot_height=400, title='temp_title')


### a alternative way to set the title, and format it
t = Title()
t.text = 'AAPL_SIRI_Scatter2'
p.title = t
p.title.text_color = 'blue'
#p.title.text_font = 'Calibri'
p.title.text_font_size = '20pt'
#p.title.text_font_style = 'italic'


### to know all the choices
#help(p)
#help(p.title)



### axies
p.yaxis.minor_tick_line_color = 'Green'

p.xaxis.axis_label = 'AAPL'
p.xaxis.axis_label_text_font_style = 'normal'
p.yaxis.axis_label = 'SIRI'
p.yaxis.axis_label_text_font_style = 'normal'


### plot different shapes
#p.triangle(df['adj_close_AAPL'], df['adj_close_SIRI'], size=range(len(df)), color='red', alpha=0.5)
#p.circle(df['adj_close_AAPL'], df['adj_close_SIRI'], size=range(len(df)), color='red', alpha=0.5)
p.line(df['date'].dt.date, df['adj_close_AAPL'], line_width=2, color='red', alpha=0.5) # alpha 是透明度
p.line(df['date'].dt.date, df['adj_close_SIRI'], line_width=2, color='green', alpha=0.5)

### out put the html file and show
output_file("E:/Work/PartTime/DQ_Project/output/graphic/test_bokeh.html")

# with mode='cdn', in the html files that it generates, it actually takes the CSS and JS script from Bokeh's website; and you can set it to 'relative' (does not work for me, it looks that it defaulted to D drive for this computer), 'absolute' (downloaded those files to local, and it worked), 'inline' (have both of the the script in the file)
#output_file("E:/Work/PartTime/DQ_Project/scripts/test_bokeh.html", mode = 'cdn')
#output_file("E:/Work/PartTime/DQ_Project/scripts/test_bokeh.html", mode = 'relative')
output_file("E:/Work/PartTime/DQ_Project/output/graphic/test_bokeh.html", mode = 'absolute')

show(p)





from bokeh.layouts import gridplot

x = df['date']
y0 = df['adj_close_AAPL']
y1 = df['adj_close_SIRI']
y2 = df['date']

# create a new plot
s1 = figure(width=250, plot_height=250)
s1.circle(x, y0, size=10, color="navy", alpha=0.5)

# create another one
s2 = figure(width=250, height=250)
s2.triangle(x, y1, size=10, color="firebrick", alpha=0.5)

# create and another
s3 = figure(width=250, height=250)
s3.square(x, y2, size=10, color="olive", alpha=0.5)

# put all the plots in a gridplot
p = gridplot([[s1, s2], [s3, None]], toolbar_location=None)

# show the results
show(p)




from bokeh.io import output_notebook, show
from bokeh.plotting import figure
from bokeh.layouts import gridplot
x = list(range(11))
y0, y1, y2 = x, [10-i for i in x], [abs(i-5) for i in x]
plot_options = dict(width=250, plot_height=250, tools='pan,wheel_zoom')
# create a new plot
s1 = figure(**plot_options)
s1.circle(x, y0, size=10, color="navy")
# create a new plot and share both ranges
s2 = figure(x_range=s1.x_range, y_range=s1.y_range, **plot_options)
s2.triangle(x, y1, size=10, color="firebrick")
# create a new plot and share only one range
s3 = figure(x_range=s1.x_range, **plot_options)
s3.square(x, y2, size=10, color="olive")
p = gridplot([[s1, s2, s3]])
# show the results
show(p)





from math import pi

import pandas as pd

from bokeh.plotting import figure, show, output_file
from bokeh.sampledata.stocks import MSFT

#bokeh.sampledata.download()

df = pd.DataFrame(MSFT)[:50]
df["date"] = pd.to_datetime(df["date"])

inc = df.close > df.open
dec = df.open > df.close
w = 12*60*60*1000 # half day in ms

TOOLS = "pan,wheel_zoom,box_zoom,reset,save"

p = figure(x_axis_type="datetime", tools=TOOLS, plot_width=1000, title = "MSFT Candlestick")
p.xaxis.major_label_orientation = pi/4
p.grid.grid_line_alpha=0.3

p.segment(df.date, df.high, df.date, df.low, color="black")
p.vbar(df.date[inc], w, df.open[inc], df.close[inc], fill_color="#D5E1DD", line_color="black")
p.vbar(df.date[dec], w, df.open[dec], df.close[dec], fill_color="#F2583E", line_color="black")

output_file("E:/Work/PartTime/DQ_Project/output/graphic/candlestick.html", title="candlestick.py example")

show(p)  # open a browser














import pandas as pd
import bokeh.plotting as bp
from bokeh.models import NumeralTickFormatter, HoverTool, Range1d, LinearAxis

df_x_series = ['a','b','c']
fig = bp.figure(title='WIP',x_range=df_x_series,plot_width=500,plot_height=300,toolbar_location='below',toolbar_sticky=False,tools=['reset','save'],active_scroll=None,active_drag=None,active_tap=None)
fig.title.align= 'center'
fig.y_range = Range1d(0, 3)
fig.extra_y_ranges = {'c_count':Range1d(start=0, end=10)}
fig.add_layout(LinearAxis(y_range_name='c_count'), 'right')
#fig.vbar(bottom=0, top=[1,2,3], x=['a','b','c'], color='blue', legend='Amt', width=0.3, alpha=0.5)
fig.line(x=['a','b','c'], y=[1,2,1], line_width=2, color='navy', alpha=0.5)
fig.vbar(bottom=0, top=[5,7,8], x=['a','b','c'], color='green', width=0.3, alpha=0.8, y_range_name='c_count')
fig.yaxis[0].formatter = NumeralTickFormatter(format='0.0')
bp.output_file('bar.html')
bp.show(fig)








from bokeh.io import output_file, show
from bokeh.layouts import widgetbox
from bokeh.models.widgets import TextInput

output_file("text_input.html")

text_input = TextInput(value="default", title="Label:")

show(widgetbox(text_input))





from bokeh.layouts import widgetbox
from bokeh.models import CustomJS, TextInput, Paragraph
from bokeh.plotting import output_file, show

# SAVE
#output_file('Sample_Application.html',mode='inline',root_dir=None)
# PREP DATA
welcome_message = 'You have selected: (none)'

# TAKE ONLY OUTPUT
text_banner = Paragraph(text=welcome_message, width=200, height=100)

# CALLBACKS
def callback_print(text_banner=text_banner):
    user_input = str(cb_obj.value)
    welcome_message = 'You have selected: ' + user_input
    text_banner.text = welcome_message
    text_file = open("Output.txt", "w")
    text_file.write(welcome_message + '\n')
    text_file.close()

# USER INTERACTIONS
text_input = TextInput(value="", title="Enter row number:",             
callback=CustomJS.from_py_func(callback_print))

# LAYOUT
widg = widgetbox(text_input, text_banner)
show(widg)







from bokeh.layouts import widgetbox
from bokeh.models import CustomJS, TextInput, Paragraph
from bokeh.plotting import output_file, show

# SAVE
#output_file('Sample_Application.html',mode='inline',root_dir=None)
# PREP DATA
welcome_message = 'You have selected: (none)'

# CALLBACKS
def callback_print(source=None, window=None):
    user_input = str(cb_obj.value)
    welcome_message = 'You have selected: ' + user_input
    source.trigger('change')

# TAKE ONLY OUTPUT
text_banner = Paragraph(text=welcome_message, width=200, height=100)

# USER INTERACTIONS
text_input = TextInput(value="", title="Enter row number:",             
callback=CustomJS.from_py_func(callback_print))

# LAYOUT
widg = widgetbox(text_input, text_banner)
show(widg)















##############################
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

# Set up data
N = 200
x = np.linspace(0, 4*np.pi, N)
y = np.sin(x)
source = ColumnDataSource(data=dict(x=x, y=y))


# Set up plot
plot = figure(plot_height=400, plot_width=400, title="my sine wave",
              tools="crosshair,pan,reset,save,wheel_zoom",
              x_range=[0, 4*np.pi], y_range=[-2.5, 2.5])

plot.line('x', 'y', source=source, line_width=3, line_alpha=0.6)


# Set up widgets
text = TextInput(title="title", value='my sine wave')
offset = Slider(title="offset", value=0.0, start=-5.0, end=5.0, step=0.1)
amplitude = Slider(title="amplitude", value=1.0, start=-5.0, end=5.0, step=0.1)
phase = Slider(title="phase", value=0.0, start=0.0, end=2*np.pi)
freq = Slider(title="frequency", value=1.0, start=0.1, end=5.1, step=0.1)


# Set up callbacks
def update_title(attrname, old, new):
    plot.title.text = text.value

text.on_change('value', update_title)

def update_data(attrname, old, new):

    # Get the current slider values
    a = amplitude.value
    b = offset.value
    w = phase.value
    k = freq.value

    # Generate the new curve
    x = np.linspace(0, 4*np.pi, N)
    y = a*np.sin(k*x + w) + b

    source.data = dict(x=x, y=y)

for w in [offset, amplitude, phase, freq]:
    w.on_change('value', update_data)


# Set up layouts and add to document
inputs = widgetbox(text, offset, amplitude, phase, freq)

curdoc().add_root(row(inputs, plot, width=800))
curdoc().title = "Sliders"













from bokeh.plotting import figure, output_file, show, ColumnDataSource
from bokeh.models import HoverTool

output_file("toolbar.html")

source = ColumnDataSource(data=dict(
    a=[1, 2, 3, 4, 5],
    b=[2, 5, 8, 2, 7],
    desc=['A', 'b', 'C', 'd', 'E'],
))

hover = HoverTool(tooltips=[
    ("index", "$index"),
    ("(a,b)", "($x, $y)"),
    ("desc", "@desc"),
    ("label", "@label"),
])

p = figure(plot_width=400, plot_height=400, tools=[hover],
           title="Mouse over the dots")

p.circle('a', 'b', size=20, source=source)

show(p)












b = Button(label='0')

def changeLabel(button):
    if button.label = '0':
        button.label= '1'
    else:
        button.label= '0'

b.on_click(lambda : changeLabel(b))