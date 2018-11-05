# -*- coding: utf-8 -*-
"""
Created on Mon Apr  2 00:58:47 2018
Last modified on 20181007 - added comments

@author: Jing Ma
"""

import pandas as pd
from datetime import timedelta

from scipy.stats import beta
#y = list(beta.pdf([0.1, 0.2, 0.3, 0.4, 0.5, 0.8, 0.9], 3, 8))

from ExecQuery import ExecQuery
from MyStatsLib import GetPdfMode
from config import RunGUI_config
data_config = RunGUI_config['data']
plot_config = RunGUI_config['plot']
#ticker = 'JNJ'

def main():
    pass


#########################################
### The Query Functions
#########################################
def QueryGUIData(data_config, ticker, data_type, normalize=False):
      
    if data_type == 'px_series':
        px_series_table = data_config['px_series_table']
        px_series_query = """select date as date_raw, adj_close as price, volume as volume_raw 
                             from """+px_series_table+""" 
                             where ticker = '"""+ticker+"""' 
                             order by ticker, date;"""
        print(px_series_query)
        px_series_df = ExecQuery(data_config['database'], px_series_query, True, True)
        
        px_series_df['date'] = pd.to_datetime(px_series_df['date_raw'], format='%Y-%m-%d') + timedelta(hours=16)
        
        volume_unit = 1e6 if px_series_df['volume_raw'].max()>1e6 else 1e3
        px_series_df['volume'] = px_series_df['volume_raw']/volume_unit
        volume_unit_str = 'M' if volume_unit==1e6 else 'K'

        return {'df':px_series_df[['date','price','volume']], 'volume_unit_str':volume_unit_str}
    
    elif data_type in ['px_dist_crude','px_dist_manual']:
        px_dist_table = data_config['px_dist_table']
        
        model = data_type.split('_')[-1]
        max_dt_subquery = """(
                                select ticker, price, max(asof_datetime) as max_dt
                                from """+px_dist_table+""" 
                                where ticker='"""+ticker+"""' 
                                and model='""" + model + """'
                                and not deprecated
                                group by 1,2
                             )"""
        px_dist_query = """ select p.price, p.prob
                            from """+px_dist_table+""" p
                            join """+max_dt_subquery+""" s 
                            on p.price=s.price and p.asof_datetime=s.max_dt #and p.ticker=s.ticker
                            where p.ticker='"""+ticker+"""' 
                            and p.model='""" + model + """'
                            and not deprecated
                            order by price
                         ;"""
        print(px_dist_query)
        px_dist_df = ExecQuery(data_config['database'], px_dist_query, True, True)
        if normalize:
            px_dist_df['prob'] = px_dist_df['prob']/px_dist_df['prob'].sum()
        return px_dist_df
    
    elif data_type in ['px_beta_dist_autol', 'px_beta_dist_autom', 'px_beta_dist_autor', 'px_beta_dist_cust']:
        #ticker = 'IBM'
        #data_type = 'px_beta_dist_autol'
        px_beta_dist_table = data_config['px_beta_dist_table']
        
        model = data_type.split('_')[-1]
        max_dt_subquery = """(
                                select ticker, max(asof_datetime) as max_dt
                                from """+px_beta_dist_table+""" 
                                where ticker='"""+ticker+"""' 
                                and model='""" + model + """'
                                and not deprecated
                                group by 1
                             )"""
        px_dist_query = """ select p.price_mode, p.price_band, p.alpha, p.beta
                            from """+px_beta_dist_table+""" p
                            join """+max_dt_subquery+""" s 
                            on p.asof_datetime=s.max_dt #and p.ticker=s.ticker
                            where p.ticker='"""+ticker+"""' 
                            and p.model='""" + model + """'
                            and not deprecated
                         ;"""
        print(px_dist_query)
        
        px_dist_base_df = ExecQuery(data_config['database'], px_dist_query, True, True)
        
        if len(px_dist_base_df)==0:
            model = 'autom'
            max_dt_subquery = """(
                        select ticker, max(asof_datetime) as max_dt
                        from """+px_beta_dist_table+""" 
                        where ticker='"""+ticker+"""' 
                        and model='""" + model + """'
                        and not deprecated
                        group by 1
                     )"""
            px_dist_query = """ select p.price_mode, p.price_band, p.alpha, p.beta
                    from """+px_beta_dist_table+""" p
                    join """+max_dt_subquery+""" s 
                    on p.asof_datetime=s.max_dt #and p.ticker=s.ticker
                    where p.ticker='"""+ticker+"""' 
                    and p.model='""" + model + """'
                    and not deprecated
                 ;"""
            px_dist_base_df = ExecQuery(data_config['database'], px_dist_query, True, True)
        
        px_mode = px_dist_base_df['price_mode'][0]
        px_band = round(px_dist_base_df['price_band'][0],2)
        a = px_dist_base_df['alpha'][0]
        b = px_dist_base_df['beta'][0]
        
        dist_mode = GetPdfMode('beta', {'alpha':a,'beta':b})
        px_lower = round(px_mode - px_band*dist_mode,2)
        px_list = [i/100.0 for i in range(int(px_lower*100), int(px_lower*100+px_band*100+1))]
        px_dist_df = pd.DataFrame.from_items([('price', px_list)])
        #px_dist_df['price_norm'] = (px_dist_df['price']-px_lower)/px_band
        px_dist_df['prob'] = beta.pdf((px_dist_df['price']-px_lower)/px_band, a, b) #pdf
        #if normalize: px_dist_df['prob'] = px_dist_df['prob']/px_dist_df['prob'].sum()
        return px_dist_df
    

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
    px_dist_dict = {'0':'0.1',
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


def InsertPxBetaDist(data_config, ticker, model, para_dict):
    # conviction should be a string that can be translated into float
    if model in ['cust']:
        insert_query = """insert into """ +data_config['px_beta_dist_table']+ """
                          select current_timestamp() as asof_datetime
                               , '"""+model+"""' as model
                               , '"""+ticker+"""' as ticker
                               , """+para_dict['price_mode']+""" as price_mode
                               , """+para_dict['price_band']+""" as price_band
                               , """+para_dict['price_shape']+""" as price_shape
                               , """+para_dict['price_skew']+""" as price_skew
                               , least(2*exp(4*"""+para_dict['price_shape']+""")-1
                                   , greatest(1,exp(4*"""+para_dict['price_shape']+""")*(1+"""+para_dict['price_skew']+"""))) 
                                   as alpha
                               , least(2*exp(4*"""+para_dict['price_shape']+""")-1
                                   , greatest(1,exp(4*"""+para_dict['price_shape']+""")*(1-"""+para_dict['price_skew']+"""))) 
                                   as beta
                               , false as deprecated; commit;
                       """
    elif model in ['autol','autom','autor','all']:
        insert_query = """insert into """ +data_config['px_beta_dist_table']+ """
                            select current_timestamp() as asof_datetime, temp.*, false
                            from
                            (
                            	(
                            		select 'autom' as model, ticker, avg(adj_close) as price_mode, 5*stddev(adj_close) as price_band
                            			, 0.5 as price_shape
                                        , 0 as price_skew
                                        , least(2*exp(4*0.5)-1, greatest(1,exp(4*0.5)*(1+0))) as alpha
                                        , least(2*exp(4*0.5)-1, greatest(1,exp(4*0.5)*(1-0))) as beta
                                    from us.equity_daily_recent_alphav
                                    where date>=current_date()- INTERVAL 60 DAY
                                    and ticker = '"""+ticker+"""'
                                    group by 1,2,5,6,7
                                )
                                union all
                                (
                            		select 'autol' as model, ticker, avg(adj_close) as price_mode, 5*stddev(adj_close) as price_band
                            			, 0.5 as price_shape
                            			, 0.5 as price_skew
                                        , least(2*exp(4*0.5)-1, greatest(1,exp(4*0.5)*(1+0.5))) as alpha
                                        , least(2*exp(4*0.5)-1, greatest(1,exp(4*0.5)*(1-0.5))) as beta
                                    from us.equity_daily_recent_alphav
                                    where date>=current_date()- INTERVAL 60 DAY
                                    and ticker = '"""+ticker+"""'
                                    group by 1,2,5,6,7
                                )
                                union all
                                (
                            		select 'autor' as model, ticker, avg(adj_close) as price_mode, 5*stddev(adj_close) as price_band
                                		  , 0.5 as price_shape
                                        , -0.5 as price_skew
                                        , least(2*exp(4*0.5)-1, greatest(1,exp(4*0.5)*(1-0.5))) as alpha
                                        , least(2*exp(4*0.5)-1, greatest(1,exp(4*0.5)*(1+0.5))) as beta
                                    from us.equity_daily_recent_alphav
                                    where date>=current_date()- INTERVAL 60 DAY
                                    and ticker = '"""+ticker+"""'
                                    group by 1,2,5,6,7
                                )
                            ) as temp
                            where model = '""" +model+ """'
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
                           """+conviction+""" as conviction, 
                           false as deprecated; commit;
                   """
    print(insert_query)
    ExecQuery(data_config['database'], insert_query, False, False)    


#########################################
### The Helper Functions
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
