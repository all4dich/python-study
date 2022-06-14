import pika
import logging


class RabbitMQ:
    def __init__(self, host, username, password):
        self._host = host
        self._username = username
        self._password = password
        self._queue_name = None

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, value):
        self._host = value

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        self._username = value

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = value

    @property
    def queue_name(self):
        return self._queue_name

    @queue_name.setter
    def queue_name(self, value):
        self._queue_name = value

    def get_channel_with_queue(self):
        credentials = pika.PlainCredentials(self.username, self.password)
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host, credentials=credentials))
        channel = connection.channel()
        channel.queue_declare(queue=self.queue_name)
        return channel

    def get_channel_with_exchange(self, exchange_name, exchange_type_name="fanout", queue_name="",
                                  queue_exclusive=True):
        logging.info(f"Get a channel with exchange '{exchange_name}', type '{exchange_type_name}'")
        credentials = pika.PlainCredentials(self.username, self.password)
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host, credentials=credentials))
        channel = connection.channel()
        channel.exchange_declare(exchange=exchange_name, exchange_type=exchange_type_name)
        target_queue_obj = channel.queue_declare(queue=queue_name, exclusive=queue_exclusive)
        target_queue_name = target_queue_obj.method.queue
        logging.info(f"Target Exchange Name: {exchange_name}")
        logging.info(f"Target Queue Name: {target_queue_name}")
        channel.queue_bind(exchange=exchange_name, queue=target_queue_name)
        return channel, target_queue_name
