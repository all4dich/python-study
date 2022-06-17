import json
import pika

from nota.modelsearch.trial_handler.message_connector import RabbitMQ, LoginServerConnector

message_exchange_name = "netspresso_modelsearch/create_agent"
message_host = "message.netspresso.ai"
message_username = "nota_modelsearch"
message_password = "dev180928"

login_server = LoginServerConnector("https://login.netspresso.ai:8888/", "sunjoo.park@nota.ai", "wyhmdywb" )
a  = login_server.login()
creat_agent_data = {
    "agent_name": "3090g-3",
    "data_path": "/tmp/",
    "user_id": "d312baaa-9f4a-4b8f-b67c-a3e3493fde6f",
    "gpus": "'\"device=0,1,2,4\"'",
    "email": "sunjoo.park@nota.ai"
}
from datetime import datetime
if __name__ == "__main__":
    start = datetime.now()
    mq_connector = RabbitMQ(host=message_host, username=message_username, password=message_password)

    def on_response(ch, method, props, body):
        a = json.loads(body.decode("utf-8"))
        if type(a).__name__ == "str":
            a = json.loads(a)
        print(a)
        print(a["status"])
        ch.close()


    mq_channel, mq_queue_name, callback_queue_name = mq_connector.get_channel_with_exchange_rpc(
        exchange_name=message_exchange_name, callback_function=on_response)
    mq_channel.basic_publish( exchange=message_exchange_name, routing_key='', body=json.dumps(creat_agent_data),
        properties=pika.BasicProperties(
            reply_to=callback_queue_name
        )
    )
    mq_channel.start_consuming()
    print("Finish")
    print(datetime.now() - start)

