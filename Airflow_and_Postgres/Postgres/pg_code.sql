create table humans_on_operations_day
(
    dt_date Date,
    wh_id INTEGER,
    office_id INTEGER,
    prodtype_id INTEGER,
    ProdTypePart_id INTEGER,
    qty_emp_prodtype INTEGER,
    qty_emp_ProdTypePart INTEGER,
    qty_all_office INTEGER,
    ch_prodtype_wh INTEGER,
    ch_ProdTypePart_wh INTEGER,
    ch_prodtype_office INTEGER,
    ch_ProdTypePart_office INTEGER,
    
    primary key (dt_date, office_id, wh_id, ProdTypePart_id, prodtype_id)
)

create schema sync;

CREATE OR REPLACE PROCEDURE sync.humans_on_operations_day_import(_src JSON)
    SECURITY DEFINER
    LANGUAGE plpgsql
AS
$$
BEGIN
INSERT INTO humans_on_operations_day AS r(dt_date,
                                          wh_id,
                                          office_id,
                                          prodtype_id,
                                          ProdTypePart_id,
                                          qty_emp_prodtype,
                                          qty_emp_ProdTypePart,
                                          qty_all_office,
                                          ch_prodtype_wh,
                                          ch_ProdTypePart_wh,
                                          ch_prodtype_office,
                                          ch_ProdTypePart_office)
SELECT s.dt_date,
       s.wh_id,
       s.office_id,
       s.prodtype_id,
       s.prodtypepart_id as ProdTypePart_id,
       s.qty_emp_prodtype,
       s.qty_emp_prodtypepart as qty_emp_ProdTypePart,
       s.qty_all_office,
       s.ch_prodtype_wh,
       s.ch_prodtypepart_wh as ch_ProdTypePart_wh,
       s.ch_prodtype_office,
       s.ch_prodtypepart_office as ch_ProdTypePart_office
FROM JSON_TO_RECORDSET(_src) AS s(dt_date Date,
                                  wh_id Integer,
                                  office_id Integer,
                                  prodtype_id Integer,
                                  prodtypepart_id Integer,
                                  qty_emp_prodtype Integer,
                                  qty_emp_prodtypepart Integer,
                                  qty_all_office Integer,
                                  ch_prodtype_wh Integer,
                                  ch_prodtypepart_wh Integer,
                                  ch_prodtype_office Integer,
                                  ch_prodtypepart_office Integer)
ON CONFLICT (dt_date, office_id, wh_id, ProdTypePart_id, prodtype_id) DO UPDATE
SET qty_emp_prodtype = EXCLUDED.qty_emp_prodtype,
    qty_emp_ProdTypePart = EXCLUDED.qty_emp_prodtypepart,
    qty_all_office = EXCLUDED.qty_all_office,
    ch_prodtype_wh = EXCLUDED.ch_prodtype_wh,
    ch_ProdTypePart_wh = EXCLUDED.ch_prodtypepart_wh,
    ch_prodtype_office = EXCLUDED.ch_prodtype_office,
    ch_ProdTypePart_office = EXCLUDED.ch_prodtypepart_office;
END;
$$;