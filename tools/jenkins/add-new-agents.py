import argparse
import pandas as pd
from datetime import datetime
from lxml import etree
import subprocess
import re
import os
from jenkins_tools.common import Jenkins
import sys

path_sep = os.path.sep

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("--path", required=True)
arg_parser.add_argument("--config-original", required=True)
arg_parser.add_argument("--username", required=True)
arg_parser.add_argument("--password", required=True)
arg_parser.add_argument("--shell-account", required=True)
arg_parser.add_argument("--shell-password", required=True)
arg_parser.add_argument("--output", default=f"{os.environ['HOME']}/temp")
arg_parser.add_argument("--jenkins-url", required=True)
args = arg_parser.parse_args()


def execute_ssh_command(ip, command):
    command = f"sshpass -p {args.shell_password} ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {args.shell_account}@{ip} '{command}'"
    output = subprocess.check_output(command, shell=True)
    return output.decode("utf8").strip()


def create_agent_config(template_file, host_name, ip_address, cores_num):
    config_temp = etree.parse(template_file)
    config_root = config_temp.getroot()
    agent_name = config_root.find("name")
    agent_name.text = host_name
    agent_description = config_root.find("description")
    agent_description.text = ip_address
    agent_launcher_cmd = config_root.find("launcher/agentCommand")
    agent_launcher_cmd.text = re.sub(r"156\.147\.\S+", ip_address, agent_launcher_cmd.text)
    bb_thread_number = int(cores_num / 2)
    bitbake_thread_element = config_root.xpath(".//string[contains(text(), '-b ')]")
    # Set BUILD_MCF_BITBAKE_THREADS's value as '-b {bb_thread_number}'
    for each_element in bitbake_thread_element:
        each_element.text = "-b %s" % bb_thread_number
    make_thread_element = config_root.xpath(".//string[contains(text(), '-p ')]")
    # Set BUILD_MCF_MAKE_THREADS's value as '-b {bb_thread_number}'
    for each_element in make_thread_element:
        each_element.text = "-p %s" % bb_thread_number
    new_agent_config = etree.tostring(config_root).decode("utf-8")
    return new_agent_config


def write_agent_config_to_file(host_name, config_text):
    output_file_path = f"{args.output}{path_sep}new-config-{host_name}.xml"
    print(f"Write to {output_file_path}")
    with open(output_file_path, "w") as f:
        f.write(config_text)
    return output_file_path


before_read = datetime.now()
df_new = pd.read_excel(args.path, sheet_name="new")
df_old = pd.read_excel(args.path, sheet_name="old")
after_read = datetime.now()
print(f"Info: time to read {args.path} = {after_read - before_read}")

ip_list_path = os.environ['HOME'] + path_sep + "ip-list.txt"
ip_list = open(ip_list_path, "w")

jenkins_connector = Jenkins(args.jenkins_url, args.username, args.password)
for a in df_new.index:
    ip = df_new.loc[a, "IP"]
    hostname = df_new.loc[a, "Hostname"].lower()
    no_of_cores = execute_ssh_command(ip, "nproc")
    print(hostname)
    agent_config = create_agent_config(args.config_original, hostname, ip, int(no_of_cores))
    config_file_path = write_agent_config_to_file(hostname, agent_config)
    try:
        subprocess.check_call(
            f"cat {config_file_path}| java -jar ~/jenkins-cli.jar -auth {args.username}:{args.password} -s  {args.jenkins_url} create-node {hostname}",
            shell=True)
        print(f"SUCCESS: Create {hostname}")
    except subprocess.CalledProcessError as err:
        msg = str(err)
        if msg.find("java.io.IOException: Premature EOF"):
            print(f"SUCCESS: Create {hostname} with EOF Exception")
        else:
            print(f"ERROR: Can not Create {hostname}")
            print(msg)
    # jenkins_connector.create_agent(hostname, agent_config)
    ip_list.write(f"{ip}\n")
ip_list.close()
