# Kafka

## Задание 1

Поднять в docker-compose, из репозитория + sasl.

Взял код из [учебного репозитория](https://github.com/tvorobev/kafka/tree/main/docker_with_sasl).

код для [docker-compose](./docker/)

в папке docker запускаем PowerShell, выполняем команду:

```shell
docker-compose -f docker-compose-kafka-sasl.yml up -d
```

после этого открываем Offset Explorer и создаем новый кластер

Cluster name: wb_practice_kafka_sasl
Bootstrap servers: 127.0.0.1:9093

во вкладке Security:

Type: SASL Plaintext

во вкладке Advanced:

SASL Mechanism: PLAIN

во вкладке JAAS Config:

```shell
org.apache.kafka.common.security.plain.PlainLoginModule required username="admin" password="admin-secret";
```

## Задание 2

Создать топик.

В Offset explorer ПКМ по Topics, ЛКМ по Create Topic

Name: topic_practice

## Задание 3

Написать python скрипт для заливки данных из небольшой таблицы клика в топик кафка в формате json.

[producer.py](./python/producer.py)
[clickhouse_connect.py](./python/clickhouse_connect.py)

## Задание 4

Программа Offset Explorer, просмотреть данные в топике.

[Data in topic](./img/Offset_Explorer_data.png "Данные в топике")

## Задание 5

Чтение из топика питоном.

[Код](./python/consumer.py)

[Recieved messages](./img/Received_messages.png "Доставленные сообщения из топика")
