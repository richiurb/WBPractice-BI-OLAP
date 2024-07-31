# Docker

## Задание 2

 Развернуть 2 контейнера через docker. Создать, перезапустить, удалить, ограничить ресурсы, установить режим автозапуска в случае перезагрузки системы. Пробросить порты. Пробросить тома.

### postgres

*Клонирование образа:*

```shell
docker pull postgres:alpine
```

*Создадим том:*

```shell
docker volume create postgres-volume-test
```

*Запустим контейнер с необходимыми условиями:*

```shell
docker run -d --name postgres-test -p 8080:8080 -v postgres-volume-test:/var/lib/postgresql/data -e POSTGRES_PASSWORD=mysecretpassword --restart=unless-stopped -m 512m postgres:alpine
```

где:\
`-d` - фоновый режим;\
`--name postgres-test` - название контейнера;\
`-p 8080:8080` - порт на хосте 8080, порт в контейнере 8080;\
`-v postgres-volume-test:/var/lib/postgresql/data` - монтируем том postgres-volume-test к /var/lib/postgresql/data в контейнере;\
`-e POSTGRES_PASSWORD=mysecretpassword` - передаем пароль через переменную окружения;\
`--restart=unless-stopped` - всегда перезапускать контейнера, кроме случая, когда он был явно остановлен пользователен;\
`-m 512m` - ограничение на 512 Мб;\
`postgres:alpine` - имя образа с тегом.

*Перезапуск контейнера:*

```shell
docker restart postgres-test
```

*Удаление контейнера:*

```shell
docker rm -f postgres-test
```

флаг `-f` нужен для принудительного удаления.

### clickhouse

*Клонирование образа:*

```shell
docker pull clickhouse/clickhouse-server
```

*Создадим том:*

```shell
docker create clickhouse-volume-test
```

*Запустим контейнер с необходимыми условиями:*

```shell
docker run -d --name test-clickhouse-server -p 8123:8123 -p 9000:9000 -v clickhouse-volume-test:/var/lib/clickhouse --ulimit nofile=262144:262144 --restart=unless-stopped -m 1g clickhouse/clickhouse-server
```

*Перезапуск контейнера:*

```shell
docker restart test-clickhouse-server
```

*Остановка контейнера:*

```shell
docker stop test-clickhouse-server
```

*Удаление контейнера:*

```shell
docker rm test-clickhouse-server
```

## Задание 3

2 контейнера через docker compose. Создать, перезапустить, удалить, ограничить ресурсы, установить режим автозапуска в случае перезагрузки системы. Пробросить порты. Пробросить тома.

### postgres в связке с pgAdmin

*Поднимаем приложение:*

```shell
docker-compose up -d
```

После этого можно открыть на локалхосте с портом 5050 страницу, в которой появится pgAdmin, который предоставляет удобный UI для работы с postgres.

*Перезапуск приложения:*

```shell
docker-compose restart
```

*Остановка и удаление приложения:*

```shell
docker-compose down
```