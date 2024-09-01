from confluent_kafka import Producer
from clickhouse_connect import select_ch
import random

config = {
    'bootstrap.servers': 'localhost:9093',  # адрес Kafka сервера
    'client.id': 'simple-producer',
    'sasl.mechanism':'PLAIN',
    'security.protocol': 'SASL_PLAINTEXT',
    'sasl.username': 'admin',
    'sasl.password': 'admin-secret'
}

producer = Producer(**config)

def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")

def send_message(topic, data):
    try:
        # Асинхронная отправка сообщения
        producer.produce(topic, data.encode('utf-8'), callback=delivery_report)
        producer.poll(0)  # Поллинг для обработки обратных вызовов
    except BufferError:
        print(f"Local producer queue is full ({len(producer)} messages awaiting delivery): try again")

sql_dict_ProdTypeParts = """
    SELECT oper_dt
         , prodtype_id
         , prodtype_code
         , 0 employee_id
         , amount
         , wh_id
         , is_credit
    FROM tarificator
    WHERE oper_dt >= toDateTime('2024-08-28 12:00:00')
      AND oper_dt < toDateTime('2024-08-28 12:01:00')
    """

topic = 'topic_practice_spark'

def get_message(sql_select):
    sql_message = select_ch(sql_select)
    result = []
    for e in sql_message:
        result.append(f"{{\"oper_dt\": \"{e[0]}\", \"prodtype_id\": {e[1]}, \"prodtype_code\": \"{e[2]}\", \"employee_id\": \"{e[3]}\", \"amount\": {round(float(e[4]) * random.uniform(0.1, 3.5), 2)}, \"wh_id\": {e[5]}, \"is_credit\": {e[6]}}}")
    return result

if __name__ == '__main__':
    message = get_message(sql_dict_ProdTypeParts)
    for e in message:
        send_message(topic, e)
    producer.flush()
