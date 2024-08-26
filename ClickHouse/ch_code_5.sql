-- Таблица на слое stg

create table stg.salary
(
    pay_id      UUID,
    pay_dt      DateTime,
    employee_id UInt32,
    currency    UInt32,
    pay_amount  Decimal(18, 2),
    dt_load     DateTime
)
engine = MergeTree
partition by toYYYYMMDD(pay_dt)
order by pay_id
comment 'Назначение выплат сотрудникам';

-- Буферная таблица

create table direct_log.salary_buf
(
    pay_id      UUID,
    pay_dt      DateTime,
    employee_id UInt32,
    currency    UInt32,
    pay_amount  Decimal(18, 2),
    dt_load     MATERIALIZED now()
)
engine = Buffer(stg, salary, 16, 10, 100, 10000, 1000000, 10000000, 100000000)
comment 'Буферная таблица для заполнения таблицы salary';