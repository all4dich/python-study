import pika

message_server_user = "nota_modelsearch"
message_server_pass = "dev180928"

host_addr = "52.78.168.231"
credentials = pika.PlainCredentials(message_server_user, message_server_pass)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=host_addr, credentials=credentials)
)
channel = connection.channel()

channel.exchange_declare(exchange='logs', exchange_type='fanout')

result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue
#queue_name = "modelsearch_email_notification"
#queue_name = "testlog1"

channel.queue_bind(exchange="logs", queue=queue_name)

print(' [*] Waiting for logs. To exit press CTRL+C')

def callback(ch, method, properties, body):
    print(" [x] %r" % body)

channel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True)

channel.start_consuming()