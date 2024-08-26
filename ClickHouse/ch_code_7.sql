insert into direct_log.salary_buf (pay_id, pay_dt, employee_id, currency, pay_amount)
values (generateUUIDv4(), toDateTime('2024-08-23 10:30:15'), 1, 810, 1000),
       (generateUUIDv4(), toDateTime('2024-08-23 10:30:47'), 2, 810, 2000),
       (generateUUIDv4(), toDateTime('2024-08-23 10:39:41'), 3, 810, 3000),
       (generateUUIDv4(), toDateTime('2024-08-23 11:31:13'), 4, 810, 4000),
       (generateUUIDv4(), toDateTime('2024-08-26 15:10:28'), 1, 810, 1800),
       (generateUUIDv4(), toDateTime('2024-08-26 15:11:11'), 5, 810, 12000),
       (generateUUIDv4(), toDateTime('2024-08-26 15:16:58'), 6, 810, 670.50)
       
       
select *, dt_load from direct_log.salary_buf

select *, dt_load from stg.salary

select *, dt_load from currently.salary