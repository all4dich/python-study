import pika
import time
import logging

loglevel = "INFO"
numeric_level = getattr(logging, loglevel.upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError("Invalid log level: %s" % loglevel)
FORMAT = "[%(levelname)s] %(asctime)s - %(name)s - %(message)s (in %(pathname)s:%(lineno)d)"
logging.basicConfig(format=FORMAT, level=numeric_level)

message_server_user = "nota_modelsearch"
message_server_pass = "dev180928"

host_addr = "message.netspresso.ai"
credentials = pika.PlainCredentials(message_server_user, message_server_pass)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=host_addr, credentials=credentials)
)
channel = connection.channel()

exchange_name = "netspresso_modelsearch/email_notification"
channel.exchange_declare(exchange=exchange_name, exchange_type='fanout')
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue
logging.info(f"Target Exchange Name: {exchange_name}")
logging.info(f"Target Queue Name: {queue_name}")

channel.queue_bind(exchange=exchange_name, queue=queue_name)

print(' [*] Waiting for logs. To exit press CTRL+C')

def callback(ch, method, properties, body):
#    sleep_time = 10
    print(" [x] %r" % body)

channel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True
)

channel.start_consuming()