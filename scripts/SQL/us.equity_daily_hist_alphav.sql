##################################################
### CREATE TABLE
##################################################

DROP TABLE us.equity_daily_hist_alphav CASCADE;

TRUNCATE TABLE us.equity_daily_hist_alphav;

CREATE TABLE us.equity_daily_hist_alphav
(
    ticker VARCHAR(20) default null,
    date date default null,
    open float default null,
    high float default null,
    low float default null,
    close float default null,
    adj_close float default null,
    volume float default null,
    cdiv float  default null,
    split_coeff float default null
);

delete from us.equity_daily_hist_alphav where date = '2018-03-27';

alter table us.equity_daily_recent_alphav rename to us.equity_daily_hist_alphav;

##################################################
### LOAD TABLE
##################################################

LOAD DATA INFILE 'E:\\Work\\PartTime\\DQ_Project\\data\\AlphaVantage\\daily_adj\\proc\\proc.20180429.csv' 
INTO TABLE us.equity_daily_hist_alphav  
COLUMNS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
ESCAPED BY '"'
LINES TERMINATED BY '\r\n'
#IGNORE 1 ROWS
;
commit;
                     
##################################################
### TESTS
##################################################
select distinct cast(date as char) from us.equity_daily_hist_alphav;

select distinct ticker from us.equity_daily_hist_alphav;

select * from us.equity_daily_hist_alphav where ticker not in (select distinct ticker from us.equity_daily_hist_alphav where date = '20180501');

select * from us.equity_daily_hist_alphav limit 10;

select * from us.equity_daily_hist_alphav where ticker = 'JNJ';

select * from us.equity_daily_hist_alphav where ticker = 'TIG';

select * from us.equity_daily_hist_alphav where date = '2018-03-27';



select max(date) as max_date, min(date) as min_date, count(*) from us.equity_daily_hist_alphav;

select date, count(*) from us.equity_daily_hist_alphav group by 1 order by 1 desc;

