-- Роль и пользователь для чтения

CREATE ROLE readonly;

GRANT show tables, select on *.* to readonly;

CREATE USER readonly IDENTIFIED WITH SHA256_password BY 'readonly' DEFAULT ROLE readonly;


-- Роль и пользователь для создания и заполнения данных в БД стейджинга(stg) 

create role stg_create_insert;

GRANT create table, insert on stg.* to stg_create_insert;
GRANT show tables, select on *.* to stg_create_insert;

CREATE USER stg_developer IDENTIFIED WITH SHA256_password BY 'stg_dev' DEFAULT ROLE stg_create_insert;