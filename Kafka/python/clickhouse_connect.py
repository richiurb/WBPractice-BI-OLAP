import datetime
import json
from clickhouse_driver import Client

with open('secrets/ch.json') as json_file:
    data = json.load(json_file)

dbname = 'default'

client = Client(data['server'][0]['host'],
                user=data['server'][0]['user'],
                password=data['server'][0]['password'],
                port=data['server'][0]['port'],
                verify=False,
                database=dbname,
                settings={"numpy_columns": False, 'use_numpy': False},
                compression=True)

def select_ch(sql_select): 
    return client.execute(sql_select)