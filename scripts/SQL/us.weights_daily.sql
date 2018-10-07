##################################################
### CREATE TABLE
##################################################

DROP TABLE us.weights_daily CASCADE;

TRUNCATE TABLE us.weights_daily;

CREATE TABLE us.weights_daily
(
    asof_datetime datetime not null,
    strategy VARCHAR(10) not null,
    date date not null,
    ticker VARCHAR(20) not null,
    weights float default 0
);


delete from us.weights_daily where date = '2018-03-27';

###alter table us.equity_daily drop column splitRatio;

##################################################
### LOAD TABLE
##################################################

insert into us.weights_daily
select * from us.weights_daily where date>= '20150101';
commit;

##################################################
### TESTS
##################################################
select distinct cast(date as char) from us.weights_daily;

select distinct ticker from us.weights_daily;

select * from us.weights_daily where ticker not in (select distinct ticker from us.weights_daily where date = '20180501');

select * from us.weights_daily limit 10;

select * from us.weights_daily where ticker = 'JNJ';

select * from us.weights_daily where ticker = 'TIG';

select * from us.weights_daily where date = '2018-03-27';


select max(date) as max_date, min(date) as min_date, count(*) from us.weights_daily;

select date, count(*) from us.weights_daily group by 1 order by 1 desc;

