import pika
import uuid
import uuid

response = None

host = "message.netspresso.ai"
user = "nota_modelsearch"
password = "dev180928"
queue_name = "rpc_queue"


def on_response(ch, method, props, body):
    if corr_id == props.correlation_id:
        response = body
    print(corr_id)
    print(props.correlation_id)
    print(response)
    ch.close()


credentials = pika.PlainCredentials(user, password)
connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, credentials=credentials))
channel = connection.channel()

# Declare receiver queue
result = channel.queue_declare(queue='', exclusive=True)
callback_queue_name = result.method.queue
# Declare input queue waiting
channel.basic_consume(queue=callback_queue_name, on_message_callback=on_response, auto_ack=True)

corr_id = str(uuid.uuid4())
channel.basic_publish(exchange='', routing_key=queue_name,
                      properties=pika.BasicProperties(
                          reply_to=callback_queue_name, correlation_id=corr_id,
                      ), body=str(uuid.uuid4()))

channel.start_consuming()
#while response is None:
#    connection.process_data_events()
#print(str(response))
