##################################################
### CREATE TABLE
##################################################

DROP TABLE us.equity_daily_recent_alphav CASCADE;

TRUNCATE TABLE us.equity_daily_recent_alphav;

CREATE TABLE us.equity_daily_recent_alphav
(
    symbol VARCHAR(20) default null,
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


ALTER TABLE us.equity_daily_recent_alphav CHANGE COLUMN ticker symbol VARCHAR(20);

ALTER TABLE us.equity_daily_hist_alphav CHANGE COLUMN ticker symbol VARCHAR(20);


delete from us.equity_daily_recent_alphav where date = '20181025';

delete from us.equity_daily_recent_alphav where date <= '20170101';

###alter table us.equity_daily drop column splitRatio;

##################################################
### LOAD TABLE
##################################################

LOAD DATA INFILE 'E:\\Work\\PartTime\\DQ_Project\\data\\AlphaVantage\\daily_adj\\proc\\proc.20180429.csv' 
INTO TABLE us.equity_daily_recent_alphav  
COLUMNS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
ESCAPED BY '"'
LINES TERMINATED BY '\r\n'
#IGNORE 1 ROWS
;

commit;

insert into us.equity_daily_hist_alphav
select * from us.equity_daily_recent_alphav where date> '20180504' and date<='20181024';
commit;

##################################################
### TESTS
##################################################
select distinct cast(date as char) from us.equity_daily_recent_alphav;

select distinct symbol from us.equity_daily_recent_alphav;

select * from us.equity_daily_recent_alphav where symbol not in (select distinct symbol from us.equity_daily_recent_alphav where date = '20180501');

select * from us.equity_daily_recent_alphav limit 10;

select * from us.equity_daily_recent_alphav where symbol = 'JNJ';

select * from us.equity_daily_recent_alphav where symbol = 'TIG';

select * from us.equity_daily_recent_alphav where date = '2018-03-27';


select max(date) as max_date, min(date) as min_date, count(*) from us.equity_daily_recent_alphav;

select max(date) as max_date, min(date) as min_date, count(*) from us.equity_daily_hist_alphav;

select date, count(*) from us.equity_daily_recent_alphav group by 1 order by 1 desc;

select date, count(*) from us.equity_daily_hist_alphav group by 1 order by 1 desc;

select date, count(*) from us.secmaster group by 1 order by 1 desc;

select * from us.secmaster where date = '20181026';