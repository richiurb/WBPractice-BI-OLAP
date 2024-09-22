CREATE USER admin_practice identified WITH sha256_password BY 'admin_practice';

GRANT CURRENT grants ON *.* TO admin_practice WITH GRANT OPTION;

CREATE TABLE IF NOT EXISTS tarificator_by_wh_hour_emp_ptype 
(
    employee_id UInt32,
    prodtype_id UInt32,
    dt_hour DateTime,
    qty UInt64,
    wh_id UInt32,
    office_id UInt32
)
engine = MergeTree
order by (dt_hour, employee_id, prodtype_id);

CREATE TABLE IF NOT EXISTS dict_ProdType
(
    prodtype_id UInt64,
    prodtype_part_id UInt16
)
engine = MergeTree
order by (prodtype_id);

CREATE database tmp;