import pika
import logging
import requests
import json

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

    def get_channel_with_queue(self, callback_function=None, callback_auto_ack=True):
        credentials = pika.PlainCredentials(self.username, self.password)
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host, credentials=credentials))
        channel = connection.channel()

        callback_queue_name: str = None
        if callback_function:
            callback_queue_result = channel.queue_declare(queue='', exclusive=True)
            callback_queue_name = callback_queue_result.method.queue
        channel.queue_declare(queue=self.queue_name)
        return channel, callback_queue_name

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

    def get_channel_with_exchange_rpc(self, exchange_name, exchange_type_name="fanout", queue_name="",
                                      queue_exclusive=True, callback_function=None, callback_auto_ack=True):
        logging.info(f"Get a channel with exchange '{exchange_name}', type '{exchange_type_name}'")
        credentials = pika.PlainCredentials(self.username, self.password)
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host, credentials=credentials))
        channel = connection.channel()

        # Callback handling
        callback_queue_name: str = None
        if callback_function:
            callback_queue_result = channel.queue_declare(queue='', exclusive=True)
            callback_queue_name = callback_queue_result.method.queue
            channel.basic_consume(queue=callback_queue_name, on_message_callback=callback_function,
                                  auto_ack=callback_auto_ack)

        # Declare the exchange
        channel.exchange_declare(exchange=exchange_name, exchange_type=exchange_type_name)
        target_queue_obj = channel.queue_declare(queue=queue_name, exclusive=queue_exclusive)
        target_queue_name = target_queue_obj.method.queue
        logging.info(f"Target Exchange Name: {exchange_name}")
        logging.info(f"Target Queue Name: {target_queue_name}")
        channel.queue_bind(exchange=exchange_name, queue=target_queue_name)
        return channel, target_queue_name, callback_queue_name


class JenkinsConnector:
    def __init__(self, host, username, password, noti_job_name=None):
        self._host = host
        self._username = username
        self._password = password
        if self._host[-1] != "/":
            self._host = f"{self._host}/"
        self._noti_job_name = noti_job_name

    @property
    def noti_job_name(self):
        return self._noti_job_name

    @noti_job_name.setter
    def noti_job_name(self, value):
        self._noti_job_name = value

    def get_crumb(self):
        crumb_url = f"{self._host}/crumbIssuer/api/json"
        r = requests.post(crumb_url, auth=(self._username, self._password))
        crumb_value = json.loads(r.text)["crumb"]
        return crumb_value

    def send_msg_to_slack(self, channel_name, message, status, noti_job_name=None):
        if noti_job_name is None:
            noti_job_name = self._noti_job_name
        job_url = f"{self._host}job/{noti_job_name.replace('/', '/job/')}"
        build_url = job_url + "/build"
        jenkins_auth = (self._username, self._password)
        """
            jenkins_crumb = get_crumb()
            headers = {'Jenkins-Crumb': jenkins_crumb}
        """
        jenkins_crumb = self.get_crumb()
        build_params = {"parameter": [
            {"name": "CHANNEL_NAME", "value": channel_name},
            {"name": "MESSAGE", "value": message},
            {"name": "STATUS", "value": status}
        ]}
        data, content_type = urllib3.encode_multipart_formdata([
            ("json", json.dumps(build_params)),
            ("Submit", "Build"),
        ])
        headers = {"Jenkins-Crumb": jenkins_crumb, "content-type": content_type}
        r = requests.post(build_url, auth=jenkins_auth, data=data, headers=headers, verify=False)
        if r.status_code in [200, 201]:
            logging.info(f"A message {message} will be delivered to {channel_name} by {job_url}")
        else:
            logging.error(f"Failed to deliver a message {message} to {channel_name} by {job_url}")


class LoginServerConnector:
    def __init__(self, url, username=None, password=None):
        self._url = url
        self._username = username
        self._password = password
        self._api_root = "api/v1/"

    def login(self):
        logging.info("Login action")
        server_url = self._url
        api_name = "login"
        api_url = f"{server_url}{self._api_root}{api_name}"
        result = requests.post(api_url, json={"username": self._username, "password": self._password})
        if result.status_code in [200, 201]:
            logging.info(f"Return the access token for a user {self._username}")
            r = json.loads(result.text)
            access_token = r['tokens']['access_token']
            # user_refresh_token = r['tokens']['refresh_token']
            # return {"access_token": user_access_token, "refresh_token": user_refresh_token}
            return access_token
        else:
            return None

    def create_agent_key(self, agent_id, auth_token=None):
        server_url = self._url
        api_name = "create_agent_key"
        api_url = f"{server_url}{self._api_root}{api_name}"
        logging.info(f"Create Agent Key for the agent {agent_id}")
        if auth_token:
            access_token = auth_token
        else:
            try:
                access_token = self.login()
            except Exception as err:
                logging.error(str(err))
                traceback.print_exc()
                return None
        result = requests.post(api_url, json={
            "tokens": {"access_token": access_token},
            "agent_id": agent_id
        })
        if result.status_code in [200, 201]:
            logging.info(f"Return the agent key for the agent {agent_id}")
            agent_info = json.loads(result.text)
            return agent_info["agent_key"]
        else:
            logging.error(f"Can't get the agent key from the server")
            logging.error(f"Status code = {result.status_code}")
            logging.error(f"Error message = {result.text}")
            return None

    def agent_login(self, agent_id, agent_key):
        api_name = "agent_key_login"
        api_url = f"{self._url}{self._api_root}{api_name}"
        result = requests.post(api_url, json={
            "agent_id": agent_id,
            "agent_key": agent_key
        })
        if result.status_code in [200, 201]:
            logging.info(f"Return the agent login  information")
            out = json.loads(result.text)
            return out["tokens"]["access_token"]
        else:
            logging.error(f"Invalid agent login information for the agent {agent_id}")
            logging.error(f"Status code = {result.status_code}")
            logging.error(f"Error message = {result.text}")
            return None

    def deactivate_agent_key(self, agent_id, auth_token=None):
        api_name = "deactivate_agent_key"
        api_url = f"{self._url}{self._api_root}{api_name}"
        access_token = None
        if not auth_token:
            access_token = self.login()
        else:
            access_token = auth_token
        result = requests.post(api_url, json={
            "tokens": {
                "access_token": access_token
            },
            "agent_id": agent_id
        })
        if result.status_code in [200, 201]:
            logging.info(f"Deactivated the agent key for the agent {agent_id}")
        else:
            logging.error(f"Invalid agent login information for the agent {agent_id}")
            logging.error(f"Status code = {result.status_code}")
            logging.error(f"Error message = {result.text}")
            return None
