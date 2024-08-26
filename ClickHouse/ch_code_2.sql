-- создание админа
CREATE USER admin_practice identified WITH sha256_password BY 'admin_practice';

-- выдача прав админу
GRANT CURRENT grants ON *.* TO admin_practice WITH GRANT OPTION;