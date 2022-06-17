import json
import pika

from nota.modelsearch.trial_handler.message_connector import RabbitMQ
from nota.modelsearch.trial_handler.message_connector import RabbitMQ, LoginServerConnector


message_exchange_name = "netspresso_modelsearch/assign_agent"
message_host = "message.netspresso.ai"
message_username = "nota_modelsearch"
message_password = "dev180928"

login_server = LoginServerConnector("https://login.netspresso.ai:8888/", "sunjoo.park@nota.ai", "wyhmdywb" )
user_access_token = login_server.login()
print(user_access_token)

agent_id = "b042023c-1f42-5867-addc-cab039d96242"
assign_agent_data = {
  "user_id": "d312baaa-9f4a-4b8f-b67c-a3e3493fde6f",
  "agent_id": agent_id,
  "project_id": "3f7205f1-9b4e-4301-8582-c5ad7ccf865f",
  "user_access_token": user_access_token
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
    mq_channel.basic_publish( exchange=message_exchange_name, routing_key='',body=json.dumps(assign_agent_data),
        properties=pika.BasicProperties(
            reply_to=callback_queue_name
        )
    )
    mq_channel.start_consuming()
    print("Finish")
    print(datetime.now() - start)

