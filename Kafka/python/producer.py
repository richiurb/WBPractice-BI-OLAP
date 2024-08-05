from confluent_kafka import Producer
from clickhouse_connect import select_ch

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
    select ProdTypePart_id
         , ProdTypePart_name
    from dict_ProdTypeParts
    limit 100
    """

topic = 'topic_practice'

def get_message(sql_select):
    sql_message = select_ch(sql_select)
    result = []
    for e in sql_message:
        result.append(f"{{\"ProdTypePart_id\": {e[0]}, \"ProdTypePart_name\": \"{e[1]}\"}}")
    return result

if __name__ == '__main__':
    message = get_message(sql_dict_ProdTypeParts)
    for e in message:
        send_message(topic, e)
    producer.flush()