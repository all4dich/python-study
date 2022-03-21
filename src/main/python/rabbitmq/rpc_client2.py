import pika
import uuid

response = None

def on_response(ch, method, props, body):
    if corr_id == props.correlation_id:
       response = body


credentials = pika.PlainCredentials("nota_modelsearch", "dev180928")
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost', credentials=credentials))

channel = connection.channel()
result = channel.queue_declare(queue='', exclusive=True)
callback_queue = result.method.queue
channel.basic_consume(
    queue=callback_queue,
    on_message_callback=on_response,
    auto_ack=True)

response = None
corr_id = str(uuid.uuid4())
channel.basic_publish(
    exchange='',
    routing_key='rpc_queue',
    properties=pika.BasicProperties(
        reply_to=callback_queue,
        correlation_id=corr_id,
    ),
    body=str(10))

channel.start_consuming()
while response is None:
    connection.process_data_events()
print(int(response))
