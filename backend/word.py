import couchdb
import pika
import time
import argparse
import json
import os

queueName = 'word'
hostToConnect = os.environ.get('RABBITMQ_ADDRES')
userName = 'user'
userPassword = 'password'

credentials = pika.PlainCredentials(userName, userPassword)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        hostToConnect, 
        5672,
        '/',
        credentials
    )
)

couch = couchdb.Server(f'http://admin:admin@{os.environ.get("COUCHDB_ADDRES")}:5984/')
print('connect succesefull')
dbname = 'word'
if dbname in couch:
    db = couch[dbname]
    print('Database exist')
else:
    db = couch.create(dbname)
    print("Database created")

channel = connection.channel()
channel.queue_declare(queue=queueName, durable=True)

def callback(ch, method, properties, body):
    doc = json.loads(body.decode("utf-8"))
    db.save(doc)
    
channel.basic_qos(prefetch_count=10)
channel.basic_consume(queue=queueName, on_message_callback=callback)
channel.start_consuming()
