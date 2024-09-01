CREATE database stg;

CREATE database currently;

CREATE database dict;

CREATE database direct_log;

-- создание админа
CREATE USER admin_practice identified WITH sha256_password BY 'admin_practice';

-- выдача прав админу
GRANT CURRENT grants ON *.* TO admin_practice WITH GRANT OPTION;

create table dict.ProdTypePartsGuide
(
    prodtype_id     UInt64,
    ProdTypePart_id UInt16
)
engine = MergeTree
order by prodtype_id

create table dict.ProdTypeParts
(
    ProdTypePart_id   UInt16,
    ProdTypePart_name String
)
engine = MergeTree
order by ProdTypePart_id

create table stg.tarificator
(
    oper_dt           DateTime,
    prodtype_id       UInt64,
    prodtype_code     LowCardinality(String),
    ProdTypePart_id   UInt16,
    ProdTypePart_name String,
    employee_id       UInt32,
    amount            Decimal(15, 2),
    wh_id             UInt16,
    is_credit         UInt8,
    dt_load           DateTime
)
engine = MergeTree
partition by toYYYYMMDD(oper_dt)
order by (oper_dt, prodtype_id, employee_id);

create table direct_log.tarificator_buf
(
    oper_dt           DateTime,
    prodtype_id       UInt64,
    prodtype_code     LowCardinality(String),
    ProdTypePart_id   UInt16,
    ProdTypePart_name String,
    employee_id       UInt32,
    amount            Decimal(15, 2),
    wh_id             UInt16,
    is_credit         UInt8,
    dt_load           MATERIALIZED now()
)
engine = Buffer(stg, tarificator, 16, 10, 100, 10000, 1000000, 10000000, 100000000)
comment 'Буферная таблица для заполнения таблицы tarificator';

create table currently.tarificator
(
    oper_dt           DateTime,
    prodtype_id       UInt64,
    prodtype_code     LowCardinality(String),
    ProdTypePart_id   UInt16,
    ProdTypePart_name String,
    employee_id       UInt32,
    amount            Decimal(15, 2),
    wh_id             UInt16,
    is_credit         UInt8,
    dt_load           DateTime
)
engine = ReplacingMergeTree()
partition by toYYYYMMDD(oper_dt)
order by (oper_dt, prodtype_id, employee_id)
ttl toStartOfDay(oper_dt) + interval 30 day;

create materialized view stg.mv_tarificator to currently.tarificator
    (
        oper_dt           DateTime,
	    prodtype_id       UInt64,
	    prodtype_code     LowCardinality(String),
	    ProdTypePart_id   UInt16,
        ProdTypePart_name String,
	    employee_id       UInt32,
	    amount            Decimal(15, 2),
	    wh_id             UInt16,
	    is_credit         UInt8,
	    dt_load           DateTime
    ) as
    select oper_dt
    	 , prodtype_id
    	 , prodtype_code
    	 , ProdTypePart_id
    	 , ProdTypePart_name
    	 , employee_id
    	 , amount
    	 , wh_id
    	 , is_credit
         , dt_load
    from stg.tarificator;