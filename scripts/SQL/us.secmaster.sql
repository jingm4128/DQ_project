##################################################
### CREATE TABLE
##################################################

DROP TABLE us.secmaster CASCADE;

TRUNCATE TABLE us.secmaster;


CREATE TABLE us.secmaster
(
    date date not null,
    exch VARCHAR(6) default null,
    symbol VARCHAR(20) default null,
    name VARCHAR(100) default null,
    lastSale float,
    marketCap float default null,
    iPOyear INT default null,
    sector VARCHAR(50) default null,
    industry VARCHAR(100) default null
);

ALTER TABLE us.secmaster CHANGE COLUMN ticker symbol VARCHAR(20);


delete from us.secmaster where date = '2018-03-27';

###alter table us.equity_daily drop column splitRatio;

##################################################
### LOAD TABLE
##################################################

# had to manually download data from the website... for now

LOAD DATA INFILE 'E:\\Work\\PartTime\\DQ_Project\\data\\Other\\secmaster\\proc\\proc.20180429.csv' 
INTO TABLE us.secmaster  
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
select distinct date from us.secmaster;

select distinct sector from us.secmaster;

select * from us.secmaster limit 10;

select * from us.secmaster where symbol = 'AAPL';

select * from us.secmaster where date = '2018-03-27';

select * from us.secmaster where date = '20180327';

select * from us.secmaster where date = '20180429' and sector = 'Health Care' order by marketCap desc limit 100;



select max(date) as max_date, min(date) as min_date, count(*) from us.secmaster;

select date, count(*) from us.secmaster group by 1 order by 1 desc;

select distinct symbol 
from us.secmaster
where date in (select max(date) from us.secmaster)
#where date = '20180430'
and sector='Health Care'
order by marketCap desc limit 100
;