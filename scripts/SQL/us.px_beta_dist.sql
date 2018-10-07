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
    price_mode float default null, -- the price that most likely can be reached, input by the user
    price_skew float default null, -- the skew as a score between -1 and 1, -1 when the mode is on the left half of the middle of the price band
    price_band float default null, -- the range of the possible prices, max_possible_price - min_possible_price
    alpha float default null, -- the default alpha 8.8
    beta float default null, -- the default beta 8.8
    deprecated boolean default False
);

delete from us.px_beta_dist where date(asof_datetime) = '2018-03-27';

delete from us.px_beta_dist where model = 'manual';

###alter table us.equity_daily drop column splitRatio;



############ share the same table used for us.px_dist, do not create again
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
select current_timestamp() as asof_datetime, temp.*, false
from
(
	(
		select 'beta_mid' as model, ticker, avg(close) as price_mode, 0 as price_skew, stddev(adj_close) as price_skew, 8.8 as alpha, 8.8 as beta
        from us.equity_daily_recent_alphav
        where date>='2018-09-01'
        group by 1,2,4,6,7
    )
    union all
    (
		select 'beta_left' as model, ticker, avg(close) as price_mode, 0.5 as price_skew, stddev(adj_close) as price_skew, 8.8 as alpha, 4.4 as beta
        from us.equity_daily_recent_alphav
        where date>='2018-09-01'
        group by 1,2,4,6,7
    )
    union all
    (
		select 'right_left' as model, ticker, avg(close) as price_mode, -0.5 as price_skew, stddev(adj_close) as price_skew, 4.4 as alpha, 8.8 as beta
        from us.equity_daily_recent_alphav
        where date>='2018-09-01'
        group by 1,2,4,6,7
    )
) as temp
;
         
         
         select * from us.equity_daily_recent_alphav limit 10;
         
update us.px_beta_dist set deprecated=True where ticker = 'JNJ' and model = 'manual' and price = 105;
 
##################################################
### TESTS
##################################################
select current_timestamp();
select date(current_timestamp());


select distinct model from us.px_beta_dist;

select * from us.px_beta_dist limit 10;

select * from us.px_beta_dist where ticker = 'JNJ';

select * from us.px_beta_dist where ticker = 'TIG';

select * from us.px_beta_dist where model = 'manual';

select * from us.px_beta_dist where date(asof_datetime) = '2018-03-27';



select max(asof_datetime) as max_date, min(asof_datetime) as min_date, count(*) from us.px_beta_dist;

select date(asof_datetime), count(*) from us.px_beta_dist group by 1 order by 1 desc;




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
