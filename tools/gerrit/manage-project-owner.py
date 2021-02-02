import argparse
from datetime import datetime
from urllib import parse
import requests
import json

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("--username", required=True, help="Gerrit Administrator Username")
arg_parser.add_argument("--password", required=True, help="Gerrit Administrator Password")
arg_parser.add_argument("--url", required=True, help="Gerrit Web Url")
arg_parser.add_argument("--project", required=True, help="Project name on Gerrit")
arg_parser.add_argument("--target-user", required=True, help="Username to be added on Owner")
arg_parser.add_argument("--remove-user", action="store_true", help="Remove a specified user from Owner")
args = arg_parser.parse_args()

gerrit_api_root = f"{args.url}a/"
gerrit_username = args.username
gerrit_password = args.password
target_user = args.target_user


def get_project_info(project_name):
    project_name_uri = parse.quote(project_name, safe="")
    get_project_url = f"{gerrit_api_root}projects/{project_name_uri}/access"
    r = requests.get(get_project_url, auth=(gerrit_username, gerrit_password))
    r_obj = json.loads(r.text.replace(")]}'", ""))
    return r_obj


def get_owner_info(project_name):
    access_info = get_project_info(project_name)
    group_info = access_info['groups']
    owner_rule = access_info['local']['refs/*']['permissions']['owner']['rules']
    owner_id = next(iter(owner_rule))
    owner_group = group_info[owner_id]
    return {"id": owner_id, "name": owner_group['name'], "url": owner_group['url']}


def add_user_to_owner_group(project_name, new_user):
    owner_info = get_owner_info(project_name)
    owner_id = owner_info["id"]
    add_member_to_group = f"{gerrit_api_root}groups/{owner_id}/members/{new_user}"
    add_member_req = requests.put(add_member_to_group, auth=(gerrit_username, gerrit_password))
    return add_member_req.status_code


def remove_user_from_owner_group(project_name, removed_user):
    owner_info = get_owner_info(project_name)
    owner_id = owner_info["id"]
    remove_group_member = f"{gerrit_api_root}groups/{owner_id}/members/{removed_user}"
    remove_member_req = requests.delete(remove_group_member, auth=(gerrit_username, gerrit_password))
    return remove_member_req.status_code


# Main Area #
return_code = ""
job_type = {True: 'Remove user', False: 'Add user'}
if args.remove_user:
    return_code = remove_user_from_owner_group(args.project, target_user)
else:
    return_code = add_user_to_owner_group(args.project, target_user)
print(f"{__file__}: Job type = {job_type[args.remove_user]}")
print(f"{__file__}: Result = {return_code}")
