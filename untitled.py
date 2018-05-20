import pandas as pd
import numpy as np
from bokeh.plotting import ColumnDataSource, figure, gmap
from bokeh.models import HoverTool, ColumnDataSource, Select, Slider, GMapOptions
from bokeh.io import output_file, show
from bokeh.layouts import row, column, widgetbox
from bokeh.io import curdoc, output_file, show
from bokeh.models.widgets import Panel, Tabs

df_clean=pd.read_csv('generation_profile.csv')
df_clean=df_clean.iloc[:,2:8]
df_clean=df_clean.drop_duplicates(subset=['ENERGY SOURCE', 'MONTH', 'STATE', 'YEAR'])
df_clean['STATE']=df_clean['STATE'].str.upper()

US_profile=df_clean[['STATE','ENERGY SOURCE','GENERATION\n(Megawatthours)','YEAR','MONTH']]
US_pivot_clean=pd.pivot_table(US_profile, values='GENERATION\n(Megawatthours)', index=['YEAR','MONTH'], columns=['ENERGY SOURCE','STATE'], aggfunc=np.sum).reset_index()
US_pivot_clean=US_pivot_clean.fillna(0)
US_pivot_clean=US_pivot_clean.sort_values(by=['YEAR', 'MONTH'])

MONTH=US_pivot_clean.loc[US_pivot_clean['YEAR']==2015]['MONTH']
NUCLEAR=US_pivot_clean.loc[US_pivot_clean['YEAR']==2015]['Nuclear']['US-TOTAL']
WIND=US_pivot_clean.loc[US_pivot_clean['YEAR']==2015]['Wind']['US-TOTAL']
source = ColumnDataSource(data={
    'x' : US_pivot_clean.loc[US_pivot_clean['YEAR']==2015]['MONTH'],
    'y' : US_pivot_clean.loc[US_pivot_clean['YEAR']==2015]['Nuclear']['US-TOTAL'],
    'y2' : US_pivot_clean.loc[US_pivot_clean['YEAR']==2015]['Wind']['US-TOTAL'],    
})

p = figure(title="Monthly Generation",x_axis_label='Month', y_axis_label='MWh',x_range=(0.5,12.5),plot_height=300,plot_width=600)
p.xaxis.ticker = [1,2,3,4,5,6,7,8,9,10,11,12]
p.line('x','y2',source=source,color='green')
p.circle('x','y2',source=source,color='green',size=10)
p.line('x','y',source=source,color='blue')
p.square('x','y',source=source,color='blue',size=10)
hoverp = HoverTool(tooltips=[('Month', '@x'),('Nuclear', '@y'),('Wind', '@y2')])
p.add_tools(hoverp)

wind15 = US_pivot_clean.loc[US_pivot_clean['YEAR'] == 2015, 'Wind']['US-TOTAL'].sum()/US_pivot_clean.loc[US_pivot_clean['YEAR'] == 2015, 'Total']['US-TOTAL'].sum()
nuclear15 = (US_pivot_clean.loc[US_pivot_clean['YEAR'] == 2015, 'Wind']['US-TOTAL'].sum()+US_pivot_clean.loc[US_pivot_clean['YEAR'] == 2015, 'Nuclear']['US-TOTAL'].sum())/US_pivot_clean.loc[US_pivot_clean['YEAR'] == 2015, 'Total']['US-TOTAL'].sum()
percents = [0,wind15,nuclear15,1]
starts = [p*2*np.pi for p in percents[:-1]]
ends = [p*2*np.pi for p in percents[1:]]
colors=['green','blue','grey']
percent2 = [wind15*100.0,(nuclear15-wind15)*100.0,(1-nuclear15)*100.0]
source1=ColumnDataSource(data={
    'starts' : starts,
    'ends' : ends,
    'colors' : colors,  
    'percents' : percent2,
})

q = figure(plot_height=300,plot_width=300)
q = figure(title="Percentage of Total Generation",x_range=(-1.2,1.2),y_range=(-1.2,1.2),plot_height=300,plot_width=300)
q.xgrid.grid_line_color = None
q.ygrid.grid_line_color = None
q.xaxis.bounds = (0, 0)
q.yaxis.bounds = (0, 0)
q.wedge(x=0,y=0,radius=1,start_angle='starts',end_angle='ends',color='colors', source=source1)
hoverq = HoverTool(tooltips=[('Percents', '@percents')])
q.add_tools(hoverq)

slider = Slider(title='Year', start=2001, end=2017, step=1, value=2015)  
select = Select(title="State Selection", options=list(df_clean['STATE'].unique()), value='US-TOTAL')

def callback(attr, old, new):
    year = slider.value
    state = select.value
    
    new_x = US_pivot_clean.loc[US_pivot_clean['YEAR']==year]['MONTH']
    new_y = US_pivot_clean.loc[US_pivot_clean['YEAR']==year]['Nuclear'][state]
    new_y2 = US_pivot_clean.loc[US_pivot_clean['YEAR']==year]['Wind'][state]
    source.data = {'x': new_x, 'y': new_y, 'y2': new_y2}
    
    new_wind15 = US_pivot_clean.loc[US_pivot_clean['YEAR'] == year, 'Wind'][state].sum()/US_pivot_clean.loc[US_pivot_clean['YEAR'] == year, 'Total'][state].sum()
    new_nuclear15 = (US_pivot_clean.loc[US_pivot_clean['YEAR'] == year, 'Wind'][state].sum()+US_pivot_clean.loc[US_pivot_clean['YEAR'] == year, 'Nuclear'][state].sum())/US_pivot_clean.loc[US_pivot_clean['YEAR'] == year, 'Total'][state].sum()
    new_percents = [0,new_wind15,new_nuclear15,1]
    new_starts = [p*2*np.pi for p in new_percents[:-1]]
    new_ends = [p*2*np.pi for p in new_percents[1:]]
    new_colors=['green','blue','grey']
    new_percent2 = [new_wind15*100.0,(new_nuclear15-new_wind15)*100.0,(1-new_nuclear15)*100.0]
    source1.data = {'starts' : new_starts, 'ends' : new_ends, 'colors' : new_colors, 'percents' : new_percent2}
    
    new_aaa=pd.date_range(start='1/1/2001', end='1/1/2018', freq='M')
    new_bbb=(US_pivot_clean['Total'][state]-US_pivot_clean['Nuclear'][state]-US_pivot_clean['Wind'][state])/1000.0
    new_ccc=new_bbb+(US_pivot_clean['Nuclear'][state]/1000.0)
    new_ddd=US_pivot_clean['Total'][state]/1000.0
    new_aaa=new_aaa.insert(0, np.min(new_aaa)).insert(205, np.max(new_aaa))
    new_bbb=pd.Series(np.min(new_bbb)).append(new_bbb).append(pd.Series(np.min(new_bbb)))
    new_ccc=pd.Series(np.min(new_bbb)).append(new_ccc).append(pd.Series(np.min(new_bbb)))
    new_ddd=pd.Series(np.min(new_bbb)).append(new_ddd).append(pd.Series(np.min(new_bbb)))
    source2.data = {'aaa' : new_aaa,'bbb' : new_bbb, 'ccc' : new_ccc,'ddd' : new_ddd}

slider.on_change('value',callback)
select.on_change('value', callback)

aaa=pd.date_range(start='1/1/2001', end='1/1/2018', freq='M')
bbb=(US_pivot_clean['Total']['US-TOTAL']-US_pivot_clean['Nuclear']['US-TOTAL']-US_pivot_clean['Wind']['US-TOTAL'])/1000.0
ccc=bbb+(US_pivot_clean['Nuclear']['US-TOTAL']/1000.0)
ddd=US_pivot_clean['Total']['US-TOTAL']/1000.0
aaa=aaa.insert(0, np.min(aaa)).insert(205, np.max(aaa))
bbb=pd.Series(np.min(bbb)).append(bbb).append(pd.Series(np.min(bbb)))
ccc=pd.Series(np.min(bbb)).append(ccc).append(pd.Series(np.min(bbb)))
ddd=pd.Series(np.min(bbb)).append(ddd).append(pd.Series(np.min(bbb)))
source2 = ColumnDataSource(data={
    'aaa' : aaa,
    'bbb' : bbb, 
    'ccc' : ccc,
    'ddd' : ddd,
})
r = figure(title="Total Energy Generation [2001-2017]",x_axis_label='Year', y_axis_label='GWh',x_range=(np.min(aaa),np.max(aaa)),x_axis_type='datetime',plot_height=300,plot_width=900)
r.patch('aaa','ddd',source=source2, color='green')
r.patch('aaa','ccc',source=source2, color='blue')
r.patch('aaa','bbb',source=source2, color='grey')

output_file("gmap.html")

windloc=pd.read_csv('uswtdb_v1_0_20180419.csv')
nuclear17=pd.read_csv('nuclear17.csv')

map_options = GMapOptions(lat=38, lng=-97, map_type="roadmap", zoom=3)


s = gmap("AIzaSyATo8VYg6pEUDkt-ZF8_lVjurmYATqbuQk", map_options, title="US Map",plot_height=600,plot_width=500)

windmap_source = ColumnDataSource(
    data=dict(lat=windloc['ylat'],
              lon=windloc['xlong'])
)

nuclearmap_source = ColumnDataSource(
    data=dict(lat=nuclear17['lat'],
              lon=nuclear17['long'])
)

s.circle(x="lon", y="lat", size=2, color="green", fill_alpha=0.8, source=windmap_source)
s.circle(x="lon", y="lat", size=5, color="blue", fill_alpha=0.8, source=nuclearmap_source)


row2 = row(p, q)
layout=column(widgetbox(slider,select),row2,r,s)
tab1 = Panel(child=layout, title="Charts")
tab2 = Panel(child=r, title="Map")

tabs = Tabs(tabs=[ tab1, tab2 ])
layout2=column(widgetbox(slider,select),tabs)
curdoc().add_root(layout)
