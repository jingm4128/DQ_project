##################################################
### CREATE TABLE
##################################################

DROP TABLE us.px_beta_dist CASCADE;

TRUNCATE TABLE us.px_beta_dist;

CREATE TABLE us.px_beta_dist
(
    asof_datetime datetime not null,
    model varchar(10) not null,
    ticker VARCHAR(20) not null,
    price_mode float default null,
    price_skew float default null,
    deprecated boolean default False
);

delete from us.px_beta_dist where date(asof_datetime) = '2018-03-27';

delete from us.px_beta_dist where model = 'manual';

###alter table us.equity_daily drop column splitRatio;


DROP TABLE us.px_dist_conviction CASCADE;

TRUNCATE TABLE us.px_dist_conviction;

CREATE TABLE us.px_dist_conviction
(
    asof_datetime datetime not null,
    model varchar(10) not null,
    ticker VARCHAR(20) not null,
    conviction float default null, # should be between 1 and 10
    deprecated boolean default False
);

delete from us.px_dist_conviction where date(asof_datetime) = '2018-03-27';

delete from us.px_dist_conviction where model = 'manual';

###alter table us.equity_daily drop column splitRatio;



##################################################
### LOAD TABLE
##################################################
insert into us.px_beta_dist
select current_timestamp() as asof_datetime, 'crude' as model, temp.*, 1 as conviction, false
from
(
	(select ticker, avg(adj_close), 0.2 from us.equity_daily_recent_alphav group by 1 order by 1,2)
	union all
	(select ticker, avg(adj_close)+0.1*stddev(adj_close), 0.1 from us.equity_daily_recent_alphav group by 1 order by 1)
	union all
	(select ticker, avg(adj_close)-0.1*stddev(adj_close), 0.1 from us.equity_daily_recent_alphav group by 1 order by 1)
	union all
	(select ticker, avg(adj_close)+0.2*stddev(adj_close), 0.08 from us.equity_daily_recent_alphav group by 1 order by 1)
	union all
	(select ticker, avg(adj_close)-0.2*stddev(adj_close), 0.08 from us.equity_daily_recent_alphav group by 1 order by 1)
	union all
	(select ticker, avg(adj_close)+0.3*stddev(adj_close), 0.06 from us.equity_daily_recent_alphav group by 1 order by 1)
	union all
	(select ticker, avg(adj_close)-0.3*stddev(adj_close), 0.06 from us.equity_daily_recent_alphav group by 1 order by 1)
	union all
	(select ticker, avg(adj_close)+0.4*stddev(adj_close), 0.05 from us.equity_daily_recent_alphav group by 1 order by 1)
	union all
	(select ticker, avg(adj_close)-0.4*stddev(adj_close), 0.05 from us.equity_daily_recent_alphav group by 1 order by 1)
	union all
	(select ticker, avg(adj_close)+0.5*stddev(adj_close), 0.04 from us.equity_daily_recent_alphav group by 1 order by 1)
	union all
	(select ticker, avg(adj_close)-0.5*stddev(adj_close), 0.04 from us.equity_daily_recent_alphav group by 1 order by 1)
	union all
	(select ticker, avg(adj_close)+0.7*stddev(adj_close), 0.03 from us.equity_daily_recent_alphav group by 1 order by 1)
	union all
	(select ticker, avg(adj_close)-0.7*stddev(adj_close), 0.03 from us.equity_daily_recent_alphav group by 1 order by 1)
	union all
	(select ticker, avg(adj_close)+1*stddev(adj_close), 0.02 from us.equity_daily_recent_alphav group by 1 order by 1)
	union all
	(select ticker, avg(adj_close)-1*stddev(adj_close), 0.02 from us.equity_daily_recent_alphav group by 1 order by 1)
	union all
	(select ticker, avg(adj_close)+1.5*stddev(adj_close), 0.012 from us.equity_daily_recent_alphav group by 1 order by 1)
	union all
	(select ticker, avg(adj_close)-1.5*stddev(adj_close), 0.012 from us.equity_daily_recent_alphav group by 1 order by 1)
	union all
	(select ticker, avg(adj_close)+2*stddev(adj_close), 0.008 from us.equity_daily_recent_alphav group by 1 order by 1)
	union all
	(select ticker, avg(adj_close)-2*stddev(adj_close), 0.008 from us.equity_daily_recent_alphav group by 1 order by 1)
) as temp
;
         
         insert into us.px_dist 
         (select current_timestamp() as datetime, 'manual' as model, 'JNJ' as ticker, 123.12 as price, 0.3 as prob, null as conviction) 
         UNION ALL (select current_timestamp() as datetime, 'manual' as model, 'JNJ' as ticker, 123.23 as price, 0.15 as prob, null as conviction); 
         commit;
         
         
update us.px_dist set deprecated=True where ticker = 'JNJ' and model = 'manual' and price = 105;
 
##################################################
### TESTS
##################################################
select current_timestamp();
select date(current_timestamp());


select distinct model from us.px_dist;

select * from us.px_dist limit 10;

select * from us.px_dist where ticker = 'JNJ';

select * from us.px_dist where ticker = 'TIG';

select * from us.px_dist where model = 'manual';

select * from us.px_dist where date(asof_datetime) = '2018-03-27';



select max(asof_datetime) as max_date, min(asof_datetime) as min_date, count(*) from us.px_dist;

select date(asof_datetime), count(*) from us.px_dist group by 1 order by 1 desc;




 select asof_datetime, p.price, p.prob, conviction
                    from us.px_dist p
                    join (
                        select ticker, price, max(asof_datetime) as max_dt
                        from us.px_dist 
                        where ticker='JNJ' 
                        and model='crude' 
                        group by 1,2
                     ) s 
                    on p.price=s.price and p.asof_datetime=s.max_dt #and p.ticker=s.ticker
                    where p.ticker='JNJ' 
                    and p.model='crude'
                    order by price
                 ;
