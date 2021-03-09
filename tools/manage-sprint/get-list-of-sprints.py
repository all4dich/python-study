import argparse
import requests
import argparse
import re
import json

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("--username", required=True)
arg_parser.add_argument("--password", required=True)
arg_parser.add_argument("--second-week", action="store_true")
args = arg_parser.parse_args()
username = args.username
password = args.password

mlt4tv_sprints = "http://collab.lge.com/main/pages/viewpage.action?pageId=1187089322"

if __name__ == "__main__":
    sample_url = "https://<domain>/rest/api/content/12345?expand=body.storage"
    page_id = "1187089322"
    page_url = f"http://collab.lge.com/main/pages/viewpage.action?pageId={page_id}"
    get_page_body = f"http://collab.lge.com/main/rest/api/content/{page_id}?expand=body.storage"
    r = requests.get(get_page_body, auth=(username, password))
    target_text = r.text.replace("</strong>", "").replace("<span>", "").replace("</span>", "")
    output = re.compile(r"2021_IR\S+\)").findall(target_text)
    i = 0
    start_week = ""
    if args.second_week:
        start_week = "-1w"
    for sprint_name in sorted(output):
        # print(i, sprint_name)
        i = i + 1
        # sprint_name = "2021_IR2SP13(3/1-3/12)"
        jira_query_url = f"http://hlm.lge.com/issue/rest/api/2/search"
        jql_query = {
            "jql": f"worklogDate > startOfWeek({start_week}) AND worklogAuthor = allessunjoo.park AND Sprint =\"{sprint_name}\""}
        r2 = requests.post(jira_query_url, auth=(username, password),
                           json=jql_query)
        a = json.loads(r2.text)
        if 'issues' in a.keys():
            for each_issue in a['issues']:
                print(sprint_name, each_issue['key'], each_issue['fields']['summary'])
