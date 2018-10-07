##################################################
### CREATE TABLE
##################################################

DROP TABLE us.equity_daily_hist_quandl CASCADE;

TRUNCATE TABLE us.equity_daily_hist_quandl;

alter table us.equity_daily rename to us.equity_daily_hist_quandl;

CREATE TABLE us.equity_daily_hist_quandl
(
    ticker VARCHAR(20) default null,
    date date default null,
    open float default null,
    high float default null,
    low float default null,
    close float default null,
    volume float default null,
    exdividend float default null,
    split_ratio float default null,
    adj_open float default null,
    adj_high float default null,
    adj_low float default null,
    adj_close float default null,
    adj_volume float default null
);

delete from us.equity_daily_hist_quandl where date = '2018-03-27';

###alter table us.equity_daily drop column splitRatio;

##################################################
### LOAD TABLE
##################################################

#LOAD HIST DATA 
LOAD DATA INFILE 'E:\\Work\\PartTime\\DQ_project\\data\\QuandlWiki\\partial\\raw\\WIKI_20180327.partial2.csv' 
INTO TABLE us.equity_daily_hist_quandl 
COLUMNS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
ESCAPED BY '"'
LINES TERMINATED BY '\n'
#IGNORE 1 ROWS
#(ticker, @date, open, high, low, close, volume, exdividend, split_ratio, adj_open, adj_high, adj_low, adj_close, adj_volume) set date = str_to_date(@date,'%Y-%M-%d'); 
;

#LOAD LATEST DATA
LOAD DATA INFILE 'E:\\Work\\PartTime\\DQ_Project\\data\\QuandlWiki\\partial\\proc\\proc_WIKI_20180327.partial.csv' 
INTO TABLE us.equity_daily_hist_quandl  
COLUMNS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
ESCAPED BY '"'
LINES TERMINATED BY '\n'
#IGNORE 1 ROWS
;

commit;
                     
##################################################
### TESTS
##################################################
select distinct date from us.equity_daily_hist_quandl;

select * from us.equity_daily_hist_quandl limit 10;

select * from us.equity_daily_hist_quandl where ticker = 'AAPL';

select * from us.equity_daily_hist_quandl where date = '2018-03-27';



select max(date) as max_date, min(date) as min_date, count(*) from us.equity_daily_hist_quandl;

select date, count(*) from us.equity_daily_hist_quandl group by 1 order by 1 desc;

