#!/usr/bin/env python
import pika
import requests

host = "message.netspresso.ai"
user = "nota_modelsearch"
password = "dev180928"
queue_name = "rpc_queue"

def on_request(ch, method, props, body):
    n = str(body)
    print(f" [.] input {n}" )
    response = f"Response: {n}"
    target_job_url = "https://scheduler.netspresso.ai/job/z-experiment/job/test-pipeline/"
    build_url = f"{target_job_url}build"
    user_name = "sunjoo-park"
    key = "1103563fa1865b07015335218c7e24b0f3"
    r = requests.post(build_url, auth=(user_name, key), verify=False)


    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id=props.correlation_id),
                     body=str(response))
    ch.basic_ack(delivery_tag=method.delivery_tag)


credentials = pika.PlainCredentials(user, password)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=host, credentials=credentials))
channel = connection.channel()

channel.queue_declare(queue=queue_name)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=queue_name, on_message_callback=on_request)
print(" [x] Awaiting RPC requests")
channel.start_consuming()
