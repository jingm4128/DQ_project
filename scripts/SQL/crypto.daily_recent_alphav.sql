##################################################
### CREATE TABLE
##################################################

DROP TABLE crypto.daily_recent_alphav CASCADE;

TRUNCATE TABLE crypto.daily_recent_alphav;

CREATE TABLE crypto.daily_recent_alphav
(
    symbol VARCHAR(10) default null,
    date date default null,
    open float default null,
    high float default null,
    low float default null,
    close float default null,
    volume float default null
);

ALTER TABLE crypto.daily_recent_alphav CHANGE COLUMN ticker symbol VARCHAR(10);


delete from crypto.daily_recent_alphav where date = '2018-03-27';

delete from crypto.daily_recent_alphav where date <= '20170101';

###alter table us.equity_daily drop column splitRatio;

##################################################
### LOAD TABLE
##################################################

LOAD DATA INFILE 'E:\\Work\\PartTime\\DQ_Project\\data\\AlphaVantage\\daily_adj\\proc\\proc.20180429.csv' 
INTO TABLE crypto.daily_recent_alphav  
COLUMNS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
ESCAPED BY '"'
LINES TERMINATED BY '\r\n'
#IGNORE 1 ROWS
;

commit;

insert into crypto.daily_recent_alphav
select * from us.equity_daily_hist_alphav where date>= '20170101';
commit;


select * from bitcoin.btcusd_minbars limit 10;

select * from bitcoin.btcusd_tick_trades limit 10;

select count(*) from bitcoin.btcusd_tick_trades limit 10;

##################################################
### TESTS
##################################################
select distinct cast(date as char) from crypto.daily_recent_alphav;

select distinct symbol from crypto.daily_recent_alphav;

select * from crypto.daily_recent_alphav where symbol not in (select distinct symbol from crypto.daily_recent_alphav where date = '20180501');

select * from crypto.daily_recent_alphav limit 10;

select * from crypto.daily_recent_alphav where symbol = 'BTC-USD';

select * from crypto.daily_recent_alphav where symbol = 'ETH-USD';

select * from crypto.daily_recent_alphav where date = '2018-03-27';


select max(date) as max_date, min(date) as min_date, count(*) from crypto.daily_recent_alphav;

select max(date) as max_date, min(date) as min_date, count(*) from us.equity_daily_hist_alphav;

select date, count(*) from crypto.daily_recent_alphav group by 1 order by 1 desc;

select date, count(*) from us.equity_daily_hist_alphav group by 1 order by 1 desc;

