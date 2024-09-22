from airflow import DAG
from airflow.operators.python import PythonOperator

from datetime import datetime, timedelta

default_args = {
    "owner": "Andreev, Urbanovich",
    "start_date": datetime(2024, 9, 21),
    "retries": 1,
    "retry_delay": timedelta(seconds=60),
}

dag = DAG(
    dag_id="report_humans_on_operations_day",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    max_active_runs=1
)


def main():
    import json
    import psycopg2
    from clickhouse_driver import Client
    
    with open('/opt/airflow/dags/keys/connect.json') as json_file:
        param_сonnect = json.load(json_file)

    client_CH = Client(
        param_сonnect['clickhouse'][0]['host'],
        user=param_сonnect['clickhouse'][0]['user'],
        password=param_сonnect['clickhouse'][0]['password'],
        port=param_сonnect['clickhouse'][0]['port'],
        verify=False,
        compression=True
    )

    client_PG = psycopg2.connect(
        host=param_сonnect['postgres'][0]['host'],
        user=param_сonnect['postgres'][0]['user'],
        password=param_сonnect['postgres'][0]['password'],
        port=param_сonnect['postgres'][0]['port'],
        database=param_сonnect['postgres'][0]['database']
    )

    client_CH.execute(f"""
        create temporary table employees_operations_by_day as
        select employee_id
            , prodtype_id
            , prodtype_part_id
            , sum(qty) qty
            , toDate(dt_hour) dt_date
            , wh_id
            , office_id
        from tarificator_by_wh_hour_emp_ptype l
        semi join
        (
            select prodtype_id
                , prodtype_part_id
            from dict_ProdType
            where prodtype_part_id in (1, 2, 3, 4, 5, 6, 7, 13)
        ) r
        on l.prodtype_id = r.prodtype_id
        where prodtype_part_id in (1, 2, 3, 4, 5, 6, 7, 13)
        group by employee_id, prodtype_id, prodtype_part_id, dt_date, wh_id, office_id
    """)

    client_CH.execute(f"""
        create temporary table humans_on_operations_day_precalc as
        select dt_date
            , wh_id
            , office_id
            , prodtype_id
            , prodtype_part_id
            , uniq(employee_id)                          qty_emp_prodtype
            , uniqIf(employee_id, qty_prodtype > 1)      ch_prodtype
            , uniqIf(employee_id, qty_ProdTypePart > 1)  ch_ProdTypePart
        from
        (
            select dt_date
                , employee_id
                , argMax(t.prodtype_id, qty)      prodtype_id
                , argMax(t.prodtype_part_id, qty)  prodtype_part_id
                , any(t.qty_prodtype)             qty_prodtype
                , any(t.qty_ProdTypePart)         qty_ProdTypePart
                , argMax(t.wh_id, qty)            wh_id
                , argMax(t.office_id, qty)        office_id
            from
            (
                select employee_id
                    , dt_date
                    , prodtype_id
                    , prodtype_part_id
                    , qty
                    , uniq(prodtype_id) over (partition by employee_id, dt_date)      qty_prodtype
                    , uniq(prodtype_part_id) over (partition by employee_id, dt_date)  qty_ProdTypePart
                    , wh_id
                    , office_id
                from employees_operations_by_day
            ) t
            group by dt_date, employee_id
        )
        group by dt_date, prodtype_part_id, prodtype_id, office_id, wh_id
        with rollup
        having prodtype_id > 0
    """)

    client_CH.execute(f"""
        drop table if exists employees_operations_by_day
    """)

    client_CH.execute(f"""
        create temporary table humans_on_operations_day_main as
        select * except (ch_prodtype, ch_ProdTypePart)
            , sum(qty_emp_prodtype)              over (partition by dt_date, office_id, wh_id, prodtype_part_id) qty_emp_ProdTypePart
            , sumIf(qty_emp_prodtype, wh_id > 0) over (partition by dt_date, office_id)                         qty_all_office
            , sum(ch_prodtype)                   over (partition by dt_date, office_id, wh_id)                  ch_prodtype_wh
            , sum(ch_ProdTypePart)               over (partition by dt_date, office_id, wh_id)                  ch_ProdTypePart_wh
            , sumIf(ch_prodtype, wh_id > 0)      over (partition by dt_date, office_id)                         ch_prodtype_office
            , sumIf(ch_ProdTypePart, wh_id > 0)  over (partition by dt_date, office_id)                         ch_ProdTypePart_office
        from humans_on_operations_day_precalc
        where office_id > 0
        union all
        select * except (ch_prodtype, ch_ProdTypePart)
            , sum(qty_emp_prodtype)              over (partition by dt_date, prodtype_part_id) qty_emp_ProdTypePart
            , sum(qty_emp_prodtype)              over (partition by dt_date)                  qty_all_office
            , sum(ch_prodtype)                   over (partition by dt_date)                  ch_prodtype_wh
            , sum(ch_ProdTypePart)               over (partition by dt_date)                  ch_ProdTypePart_wh
            , sum(ch_prodtype)                   over (partition by dt_date)                  ch_prodtype_office
            , sum(ch_ProdTypePart)               over (partition by dt_date)                  ch_ProdTypePart_office
        from humans_on_operations_day_precalc
        where office_id = 0
    """)

    client_CH.execute(f"""
        drop table if exists humans_on_operations_day_precalc
    """)

    df = client_CH.query_dataframe(f"""
        select dt_date
            , toInt32(wh_id) wh_id
            , toInt32(office_id) office_id
            , toInt32(prodtype_id) prodtype_id
            , toInt32(prodtype_part_id) prodtypepart_id
            , toInt32(qty_emp_prodtype) qty_emp_prodtype
            , toInt32(qty_emp_ProdTypePart) qty_emp_prodtypepart
            , toInt32(qty_all_office) qty_all_office
            , toInt32(ch_prodtype_wh) ch_prodtype_wh
            , toInt32(ch_ProdTypePart_wh) ch_prodtypepart_wh
            , toInt32(ch_prodtype_office) ch_prodtype_office
            , toInt32(ch_ProdTypePart_office) ch_prodtypepart_office
        from humans_on_operations_day_main
    """)

    client_CH.execute(f"""
        drop table if exists humans_on_operations_day_main
    """)

    df = df.to_json(orient='records', date_format='iso')

    cursor = client_PG.cursor()
    cursor.execute(f"CALL sync.humans_on_operations_day_import(_src := '{df}')")
    client_PG.commit()

    cursor.close()
    client_PG.close()

    client_CH.disconnect()

task1 = PythonOperator(
    task_id="report_humans_on_operations_day",
    python_callable=main,
    dag=dag
)