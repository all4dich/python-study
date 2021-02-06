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
arg_parser.add_argument("--job-config", required=True)
args = arg_parser.parse_args()

api_token = "11cde0fe5bc41580d9e7c7e6f6f06afaab"
password = "admin"


class JenkinsTest:
    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password

    def create_freestyle_job(self, job_name):
        create_url = self.url + "createItem"
        create_headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        json_data = {"name": job_name, "mode": "hudson.model.FreeStyleProject"}
        r = requests.post(create_url, auth=(self.username, self.password), data=json_data, headers=create_headers)
        print(f"{__name__}:{r.status_code}")

    def create_freestyle_job_crumb(self, job_name):
        create_url = self.url + "createItem"
        crumb_url = f"{self.url}crumbIssuer/api/json"
        crumb_res = requests.get(url=crumb_url, auth=(self.username, self.password))
        crumb_json = json.loads(crumb_res.text)
        print(crumb_json)
        create_headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            crumb_json['crumbRequestField']: crumb_json['crumb']
        }
        print(create_headers)
        json_data = {"name": job_name, "mode": "hudson.model.FreeStyleProject"}
        r = requests.post(create_url, auth=(self.username, self.password), data=json_data, headers=create_headers)
        print(f"{__name__}:{r.status_code}")

    def update_job_config(self, job_name, data):
        job_url = args.jenkins_url + "job/" + job_name
        job_config_url = job_url + "/config.xml"
        headers = {"content-type": "application/xml"}
        job_update_req = requests.post(job_config_url, auth=("admin", api_token), data=data, headers=headers)
        print(job_update_req.status_code)


if __name__ == "__main__":
    # j_connector = JenkinsTest(url=args.jenkins_url, username=args.username, password=password)
    job_config_path = args.job_config
    jenkins = Jenkins(url=args.jenkins_url, username=args.username, password=api_token)
    with open(job_config_path, "r") as f:
        content = str(f.read())
        j_connector = JenkinsTest(url=args.jenkins_url, username=args.username, password=api_token)
        j_connector.create_freestyle_job("you-admin")
        j_connector.update_job_config("you-admin", content)
        j_connector.create_freestyle_job_crumb("you-admin-crumb")
        j_connector.update_job_config("you-admin-crumb", content)
        jenkins.create_job("job3", content)
