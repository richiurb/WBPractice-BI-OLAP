create table currently.salary
(
    pay_id      UUID,
    pay_dt      DateTime,
    employee_id UInt32,
    currency    UInt32,
    pay_amount  Decimal(18, 2),
    dt_load     DateTime
)
engine = ReplacingMergeTree(employee_id)
partition by toYYYYMMDD(pay_dt)
order by pay_id
ttl toStartOfDay(pay_dt) + interval 30 day
comment 'Таблица последних действий сотрудников, совершенных на складе';

create materialized view stg.mv_salary to currently.salary
    (
        pay_id      UUID,
	    pay_dt      DateTime,
	    employee_id UInt32,
	    currency    UInt32,
	    pay_amount  Decimal(18, 2),
	    dt_load     DateTime
    ) as
    select pay_id
    	 , pay_dt
    	 , employee_id
    	 , currency 
    	 , pay_amount
    	 , dt_load
    from stg.salary;