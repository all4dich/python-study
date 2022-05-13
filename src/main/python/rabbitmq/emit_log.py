#!/usr/bin/env python
import datetime

import pika
import sys
import json

message_server_user = "nota_modelsearch"
message_server_pass = "dev180928"

host_addr = "message.netspresso.ai"
exchange_name = "modelsearch_events"

credentials = pika.PlainCredentials(message_server_user, message_server_pass)

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=host_addr, credentials=credentials))
channel = connection.channel()

channel.exchange_declare(exchange=exchange_name, exchange_type='fanout')

message = {"event": "stop", "project_uid": "test_from_jenkins", "username": "username"}
channel.basic_publish(exchange=exchange_name, routing_key='', body=json.dumps(message))
print(" [x] Sent %r" % message)
connection.close()
