import argparse
from datetime import datetime
from urllib import parse
import requests
import json

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("--username", required=True)
arg_parser.add_argument("--password", required=True)
arg_parser.add_argument("--url", required=True)
arg_parser.add_argument("--project", required=True)
arg_parser.add_argument("--target-user", required=True)
arg_parser.add_argument("--remove-user", action="store_true")
args = arg_parser.parse_args()

gerrit_api_root = f"{args.url}a/"
gerrit_username = args.username
gerrit_password = args.password
target_user = args.target_user


def get_owner_info(access_info_str):
    access_info = json.loads(access_info_str)
    group_info = access_info['groups']
    owner_rule = access_info['local']['refs/*']['permissions']['owner']['rules']
    owner_id = next(iter(owner_rule))
    owner_group = group_info[owner_id]
    return {"id": owner_id, "name": owner_group['name'], "url": owner_group['url']}


def add_user_to_owner_group(access_info_str):
    owner_info = get_owner_info(access_info_str)
    owner_id = owner_info["id"]
    add_member_to_group = f"{gerrit_api_root}groups/{owner_id}/members/{target_user}"
    add_member_req = requests.put(add_member_to_group, auth=(gerrit_username, gerrit_password))
    return add_member_req.status_code


def remove_user_from_owner_group(access_info_str):
    owner_info = get_owner_info(access_info_str)
    owner_id = owner_info["id"]
    remove_group_member = f"{gerrit_api_root}groups/{owner_id}/members/{target_user}"
    remove_member_req = requests.delete(remove_group_member, auth=(gerrit_username, gerrit_password))
    return remove_member_req.status_code


# Main Area #
project_name = parse.quote(args.project, safe="")
get_project_url = f"{gerrit_api_root}projects/{project_name}/access"
r = requests.get(get_project_url, auth=(gerrit_username, gerrit_password))
if r.status_code == 200:
    print(r.text)
    if args.remove_user:
        remove_user_from_owner_group(r.text.replace(")]}'", ""))
    else:
        add_user_to_owner_group(r.text.replace(")]}'", ""))
