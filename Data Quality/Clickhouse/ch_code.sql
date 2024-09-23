CREATE database dq;

CREATE TABLE dq.tarificator_by_wh_hour_emp_ptype_dq ENGINE = ReplacingMergeTree ORDER BY dt_hour AS
SELECT dt_hour
     , count(*) all_qty
     , uniq(employee_id, prodtype_id, office_id, wh_id) uniq_qty
     , countIf(employee_id, employee_id <= 0) fail_employee_qty
     , countIf(prodtype_id, prodtype_id <= 0) fail_prodtype_qty
     , countIf(qty, qty <= 0) fail_qty_qty
     , countIf(wh_id, wh_id <= 0) fail_wh_qty
     , countIf(office_id, office_id <= 0) fail_office_qty
FROM tarificator_by_wh_hour_emp_ptype t
GROUP BY dt_hour
ORDER BY dt_hour desc