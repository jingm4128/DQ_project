##################################################
### CREATE TABLE
##################################################

DROP TABLE us.px_beta_dist CASCADE;

TRUNCATE TABLE us.px_beta_dist;

CREATE TABLE us.px_beta_dist
(
    asof_datetime datetime not null,
    model varchar(10) not null,
    symbol VARCHAR(20) not null,
    price_mode float default null, -- the price that most likely can be reached, input by the user
    price_band float default null, -- the range of the possible prices, max_possible_price - min_possible_price
    price_shape float default null, -- the parameter between 0-1 that the user put in to defined the shape of the distribution, 0 means flat and 1 means very sharp
	price_skew float default null, -- the skew as a score between -1 and 1, -1 when the mode is on the left half of the middle of the price band
    alpha float default null, -- the alpha: define a0 = exp(4*price_shape), alpha = min(2*a0-1, max(1,a0*(1+price_skew)))
    beta float default null, -- the beta: define a0 = exp(4*price_shape), alpha = min(2*a0-1, max(1,a0*(1-price_skew)))
    deprecated boolean default False
);

delete from us.px_beta_dist where date(asof_datetime) = '2018-03-27';

delete from us.px_beta_dist where model = 'manual';

###alter table us.equity_daily drop column splitRatio;

ALTER TABLE us.px_beta_dist CHANGE COLUMN ticker symbol VARCHAR(20);

alter table us.px_beta_dist alter column symbol rename to symbol;

select exp(4), greatest(1,2);

############ share the same table used for us.px_dist, do not create again
DROP TABLE us.px_dist_conviction CASCADE;

TRUNCATE TABLE us.px_dist_conviction;

CREATE TABLE us.px_dist_conviction
(
    asof_datetime datetime not null,
    model varchar(10) not null,
    symbol VARCHAR(20) not null,
    conviction float default null, # should be between 1 and 10
    deprecated boolean default False
);

delete from us.px_dist_conviction where date(asof_datetime) = '2018-03-27';

delete from us.px_dist_conviction where model = 'manual';

select * from us.px_dist_conviction;

###alter table us.equity_daily drop column splitRatio;


##################################################
### LOAD TABLE
##################################################
insert into us.px_beta_dist
select current_timestamp() as asof_datetime, temp.*, false
from
(
	(
		select 'autom' as model, symbol, avg(adj_close) as price_mode, 5*stddev(adj_close) as price_band
			, 0.5 as price_shape
            , 0 as price_skew
            , least(2*exp(4*0.5)-1, greatest(1,exp(4*0.5)*(1+0))) as alpha
            , least(2*exp(4*0.5)-1, greatest(1,exp(4*0.5)*(1-0))) as beta
        from us.equity_daily_recent_alphav
        where date>='2018-06-01'
        group by 1,2,5,6,7
    )
    union all
    (
		select 'autol' as model, symbol, avg(adj_close) as price_mode, 5*stddev(adj_close) as price_band
			, 0.5 as price_shape
			, 0.5 as price_skew
            , least(2*exp(4*0.5)-1, greatest(1,exp(4*0.5)*(1+0.5))) as alpha
            , least(2*exp(4*0.5)-1, greatest(1,exp(4*0.5)*(1-0.5))) as beta
        from us.equity_daily_recent_alphav
        where date>='2018-06-01'
        group by 1,2,5,6,7
    )
    union all
    (
		select 'autor' as model, symbol, avg(adj_close) as price_mode, 5*stddev(adj_close) as price_band
			, 0.5 as price_shape
            , -0.5 as price_skew
            , least(2*exp(4*0.5)-1, greatest(1,exp(4*0.5)*(1-0.5))) as alpha
            , least(2*exp(4*0.5)-1, greatest(1,exp(4*0.5)*(1+0.5))) as beta
        from us.equity_daily_recent_alphav
        where date>='2018-06-01'
        group by 1,2,5,6,7
    )
) as temp
;

select current_date(), current_date()-90, current_date()- INTERVAL 30 DAY;


		select 'auto_r' as model, symbol, avg(adj_close) as price_mode, 2*stddev(adj_close) as price_band, -0.5 as price_skew, 4.4 as alpha, 8.8 as beta
        from us.equity_daily_recent_alphav
        where date>='2018-06-01'
        group by 1,2,5,6,7;   
         
         select * from us.equity_daily_recent_alphav where date>='2018-09-01' limit 10;
         
update us.px_beta_dist set deprecated=True where symbol = 'JNJ' and model = 'manual' and price = 105;
 
##################################################
### TESTS
##################################################
select current_timestamp();
select date(current_timestamp());


select distinct model from us.px_beta_dist;

select * from us.px_beta_dist limit 10;

select * from us.px_beta_dist where symbol = 'JNJ';

select * from us.px_beta_dist where symbol = 'TIG';

select * from us.px_beta_dist where model = 'manual';

select * from us.px_beta_dist where date(asof_datetime) = '2018-03-27';



select max(asof_datetime) as max_date, min(asof_datetime) as min_date, count(*) from us.px_beta_dist;

select date(asof_datetime), count(*) from us.px_beta_dist group by 1 order by 1 desc;

# asof_datetime, model, symbol, price_mode, price_band, price_shape, price_skew, alpha, beta, deprecated
'2018-10-07 01:53:22', 'auto_m', 'JNJ', '122.19', '2.73031', '0', '0.5', '7.38906', '7.38906', '0'
'2018-10-07 01:53:22', 'auto_l', 'JNJ', '122.19', '2.73031', '0.5', '0.5', '11.0836', '3.69453', '0'
'2018-10-07 01:53:22', 'auto_r', 'JNJ', '122.19', '2.73031', '-0.5', '0.5', '3.69453', '11.0836', '0'



select asof_datetime, p.price, p.prob, conviction
from us.px_beta_dist p
join (
	select symbol, price, max(asof_datetime) as max_dt
	from us.px_beta_dist 
	where symbol='JNJ' 
	and model='crude' 
	group by 1,2
 ) s 
on p.price=s.price and p.asof_datetime=s.max_dt #and p.symbol=s.symbol
where p.symbol='JNJ' 
and p.model='crude'
order by price
;
