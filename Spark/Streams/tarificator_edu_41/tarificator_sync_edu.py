from pyspark.sql import *
from pyspark.sql.functions import *
from pyspark.sql.types import *
from clickhouse_driver import Client

import os
import pandas as pd
import json
from datetime import datetime
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# Нужно указать, чтобы spark подгрузил lib для kafka.
os.environ['PYSPARK_SUBMIT_ARGS'] = '--jars org.apache.spark:spark-sql-kafka-0-10_2.12-3.5.0 --packages org.apache.spark:spark-sql-kafka-0-10_2.12-3.5.0 pyspark-shell'

# Загружаем конекты. Не выкладываем в гит файл с конектами.
with open('/opt/spark/Streams/credentials_example.json') as json_file:
    сonnect_settings = json.load(json_file)

ch_db_name = "direct_log"
ch_dst_table = "tarificator_buf"

client = Client(сonnect_settings['ch_local'][0]['host'],
                user=сonnect_settings['ch_local'][0]['user'],
                password=сonnect_settings['ch_local'][0]['password'],
                verify=False,
                database=ch_db_name,
                settings={"numpy_columns": True, 'use_numpy': True},
                compression=True)

# Разные переменные, задаются в params.json
spark_app_name = "tarificator_edu"
spark_ui_port = "8081"

kafka_host = сonnect_settings['kafka_local'][0]['host']
kafka_port = сonnect_settings['kafka_local'][0]['port']
kafka_user = сonnect_settings['kafka_local'][0]['user']
kafka_password = сonnect_settings['kafka_local'][0]['password']
kafka_topic = "topic_practice_spark"
kafka_batch_size = 10000
processing_time = "15 second"

checkpoint_path = f'/opt/kafka_checkpoint_dir/{spark_app_name}/{kafka_topic}/v6'

# Создание сессии спарк.
spark = SparkSession \
    .builder \
    .appName(spark_app_name) \
    .config('spark.ui.port', spark_ui_port)\
    .config("spark.dynamicAllocation.enabled", "false") \
    .config("spark.executor.cores", "1") \
    .config("spark.task.cpus", "1") \
    .config("spark.num.executors", "1") \
    .config("spark.executor.instances", "1") \
    .config("spark.default.parallelism", "1") \
    .config("spark.cores.max", "1") \
    .config('spark.ui.port', spark_ui_port)\
    .getOrCreate()

# убираем разные Warning.
spark.sparkContext.setLogLevel("WARN")
spark.conf.set("spark.sql.adaptive.enabled", "false")
spark.conf.set("spark.sql.debug.maxToStringFields", 500)

# Описание как создается процесс spark structured streaming.
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", f"{kafka_host}:{kafka_port}") \
    .option("subscribe", kafka_topic) \
    .option("maxOffsetsPerTrigger", kafka_batch_size) \
    .option("startingOffsets", "earliest") \
    .option("failOnDataLoss", "false") \
    .option("forceDeleteTempCheckpointLocation", "true") \
    .option("kafka.sasl.jaas.config", f'org.apache.kafka.common.security.plain.PlainLoginModule required username="{kafka_user}" password="{kafka_password}";') \
    .option("kafka.sasl.mechanism", "PLAIN") \
    .option("kafka.security.protocol", "SASL_PLAINTEXT") \
    .load()

# Колонки, которые писать в ClickHouse. В kafka много колонок, не все нужны. Этот tuple нужен перед записью в ClickHouse.
columns_to_ch = ("oper_dt", "prodtype_id", "prodtype_code", "employee_id", "amount", "wh_id", "is_credit")

# Схема сообщений в топике kafka. Используется при формировании batch.
schema = StructType([
    StructField("oper_dt", StringType(), False),
    StructField("prodtype_id", LongType(), False),
    StructField("prodtype_code", StringType(), False),
    StructField("employee_id", LongType(), False),
    StructField("amount", DecimalType(15, 2), False),
    StructField("wh_id", LongType(), False),
    StructField("is_credit", BooleanType(), False),
])

sql_tmp_create = """create table tmp.tarificator_edu
    (
        oper_dt           DateTime,
        prodtype_id       UInt64,
        prodtype_code     LowCardinality(String),
        employee_id       UInt32,
        amount            Decimal(15, 2),
        wh_id             UInt16,
        is_credit         UInt8
    )
        engine = Memory
"""

sql_insert = f"""insert into {ch_db_name}.{ch_dst_table}
    select t1.oper_dt            oper_dt
         , t1.prodtype_id        prodtype_id
         , t1.prodtype_code      prodtype_code
         , ptpg.ProdTypePart_id  ProdTypePart_id
         , ptp.ProdTypePart_name ProdTypePart_name
         , t1.employee_id        employee_id
         , t1.amount             amount
         , t1.wh_id              wh_id
         , t1.is_credit          is_credit
    from tmp.tarificator_edu t1
    left any join dict.ProdTypePartsGuide ptpg
    on t1.prodtype_id = ptpg.prodtype_id
    left any join dict.ProdTypeParts ptp
    on ptpg.ProdTypePart_id = ptp.ProdTypePart_id
"""

client.execute("drop table if exists tmp.tarificator_edu")

def column_filter(df):
    # select только нужные колонки.
    col_tuple = []
    for col in columns_to_ch:
        col_tuple.append(f"value.{col}")
    return df.selectExpr(col_tuple)


def load_to_ch(df):
    # Преобразуем в dataframe pandas и записываем в ClickHouse.
    df_pd = df.toPandas()
    df_pd.oper_dt = pd.to_datetime(df_pd.oper_dt, format='ISO8601', utc=True, errors='ignore')
    df_pd.is_credit = df_pd.is_credit.astype(bool)

    client.insert_dataframe('INSERT INTO tmp.tarificator_edu VALUES', df_pd)

# Функция обработки batch. На вход получает dataframe-spark.
def foreach_batch_function(df2, epoch_id):
    df_rows = df2.count()
    # Если dataframe не пустой, тогда продолжаем.
    print(df2.count())

    if df_rows > 0:
        #df2.printSchema()
        #df2.show(5)

        # Убираем не нужные колонки.
        df2 = column_filter(df2)

        client.execute(sql_tmp_create)

        # Записываем dataframe в ch.
        load_to_ch(df2)

        # Добавляем объем и записываем в конечную таблицу.
        client.execute(sql_insert)
        client.execute("drop table if exists tmp.tarificator_edu")

# Описание как создаются микробатчи. processing_time - задается вначале скрипта
query = df.select(from_json(col("value").cast("string"), schema).alias("value")) \
    .writeStream \
    .trigger(processingTime=processing_time) \
    .option("checkpointLocation", checkpoint_path) \
    .foreachBatch(foreach_batch_function) \
    .start()

query.awaitTermination()
