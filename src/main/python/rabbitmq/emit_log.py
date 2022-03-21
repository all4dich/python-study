#!/usr/bin/env python
import datetime

import pika
import sys

message_server_user = "nota_modelsearch"
message_server_pass = "dev180928"

host_addr = "52.78.168.231"
credentials = pika.PlainCredentials(message_server_user, message_server_pass)

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=host_addr, credentials=credentials))
channel = connection.channel()

channel.exchange_declare(exchange='logs', exchange_type='fanout')

message = ' '.join(sys.argv[1:]) or f"info: Hello World!{datetime.datetime.now()}"
channel.basic_publish(exchange='logs', routing_key='', body=message)
print(" [x] Sent %r" % message)
connection.close()