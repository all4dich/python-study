import argparse
import pandas as pd
from datetime import datetime
from lxml import etree
import subprocess
import re
import os
from jenkins_tools.common import Jenkins
import sys
import json
import requests
import time

path_sep = os.path.sep

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("--username", required=True)
arg_parser.add_argument("--password", required=True)
arg_parser.add_argument("--jenkins-url", required=True)
arg_parser.add_argument("--node-name", required=True)
arg_parser.add_argument("--node-ip", required=True)
args = arg_parser.parse_args()

# https://support.cloudbees.com/hc/en-us/articles/115003896171-Creating-node-with-the-REST-API
node_name = args.node_name
node_ip = args.node_ip
node_type = "hudson.slaves.DumbSlave"
agent_data = {
    "name": node_name,
    "nodeDescription": node_ip,
    "numExecutors": "1",
    "remoteFS": "/tmp/",
    "labelString": "do-not-use",
    "mode": "NORMAL",
    "launcher": {
        "stapler-class": "hudson.slaves.CommandLauncher",
        "command": f"/binary/build_results/tools/agent_connect.sh {node_ip}"
    },
    "retentionStrategy": {
        "stapler-class": "hudson.slaves.RetentionStrategy$Always",
        "$class": "hudson.slaves.RetentionStrategy$Always"
    },
    "nodeProperties": {
        "stapler-class-bag": "true",
        "hudson-slaves-EnvironmentVariablesNodeProperty": {
            "env": {
                "key": "you_name", "value": "you_value"
            }
        }
    },
    "type": node_type
}
agent_data_new = {
    'name': node_name,
    'nodeDescription': node_ip,
    'numExecutors': '1',
    'remoteFS': '/tmp/',
    'labelString': 'do-not-use',
    'mode': 'NORMAL',
    'launcher': {
        'stapler-class': 'hudson.slaves.CommandLauncher',
        'command': '/binary/build_results/tools/agent_connect.sh ' + node_ip,
    },
    'retentionStrategy': {
        'stapler-class': 'hudson.slaves.RetentionStrategy$Always',
        '$class': 'hudson.slaves.RetentionStrategy$Always'
    },
    'nodeProperties': {
        'stapler-class-bag': 'true',
        'hudson-slaves-EnvironmentVariablesNodeProperty': {
            'env': {
                'key': 'you_name', 'value': 'you_value'
            }
        }
    },
    'type': node_type
}

# url = f"{args.jenkins_url}computer/doCreateItem?name=testnode"
create_node_url = f"{args.jenkins_url}computer/doCreateItem"
create_node_url_2 = f"{args.jenkins_url}computer/doCreateItem?name={node_name}&type={node_type}"
delete_node_url = f"{args.jenkins_url}computer/{node_name}/doDelete"
headers = {'Content-Type': 'application/x-www-form-urlencoded'}
config = {
    "name": node_name,
    "type": node_type,
    "json": json.dumps(agent_data_new)
}
config_2nd = {
    "json": json.dumps(agent_data_new)
}
config_str = json.dumps(config)
auth_info = (args.username, args.password)
r_delete = requests.post(delete_node_url, auth=auth_info)
print(r_delete)
print("Wait for 4 seconds ")
time.sleep(4)
# r = requests.post(create_node_url, headers=headers, auth=auth_info, data=config)
# r = requests.post(create_node_url_2, headers=headers, auth=auth_info, data=config_2nd)
# print(r.status_code)
jenkins_connector = Jenkins(url=args.jenkins_url, username=args.username, password=args.password)
jenkins_connector.create_agent(agent_name=node_name, agent_type=node_type, data=config_2nd)
