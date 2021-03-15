import requests
import argparse
import re
import json
from datetime import datetime, timedelta
import pandas as pd
import os
from urllib.parse import quote

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("--username", required=True)
arg_parser.add_argument("--password", required=True)
arg_parser.add_argument("--jira-url", required=True)
arg_parser.add_argument("--confluence-url", required=True)
arg_parser.add_argument("--confluence-space-key", required=True)
arg_parser.add_argument("--parent-page-id", required=True)
arg_parser.add_argument("--second-week", action="store_true")

args = arg_parser.parse_args()
username = args.username
password = args.password

jira_url = args.jira_url
confluence_url = args.confluence_url
mlt4tv_sprints = f"{confluence_url}pages/viewpage.action?pageId=1187089322"

today = datetime.now().astimezone()
local_tz = today.tzinfo
# Current Week
curr_week_start = today - timedelta(days=today.weekday())
# curr_week_end: Friday
curr_week_end = curr_week_start + timedelta(days=4)
# Previous Week
pre_week_start = today - timedelta(weeks=1, days=today.weekday())
# curr_week_end: Friday
pre_week_end = pre_week_start + timedelta(days=4)


def get_issue_info(url, username, password, issue_key):
    get_issue_info_url = f"{url}rest/api/2/issue/{issue_key}"
    r = requests.get(get_issue_info_url, auth=(username, password))
    issue_info = json.loads(r.text)
    return issue_info


def get_confluence_user_info(url, username, password):
    # https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-users/#api-rest-api-3-user-get
    # https://developer.atlassian.com/cloud/confluence/rest/api-group-users/#api-api-user-current-get
    get_user_info_url = f"{url}rest/api/user/current"
    r = requests.get(get_user_info_url, auth=(username, password))
    return json.loads(r.text)


def get_hlm_jira_link(issue_key):
    template_str = "<ac:structured-macro ac:name=\"jira\" ac:schema-version=\"1\" ac:macro-id=\"96271a36-c3f9-4963-b74a-d683f9a1fc65\">" \
                   "<ac:parameter ac:name=\"server\">HLM Tracker</ac:parameter>" \
                   "<ac:parameter ac:name=\"serverId\">b2a4479c-d518-39ac-bbdc-b8434e95443c</ac:parameter>" \
                   f"<ac:parameter ac:name=\"key\">{issue_key}</ac:parameter>" \
                   "</ac:structured-macro>"
    return template_str


def get_work_logs_from_previous_week(url, username, password, issue_key):
    output = []
    #             get_issue_worklog_url = f"{self._api_root}issue/{each_issue['key']}/worklog"
    get_worklog_url = f"{url}rest/api/2/issue/{issue_key}/worklog"
    r = requests.get(get_worklog_url, auth=(username, password))
    r_body = json.loads(r.text)
    work_logs = json.loads(r.text)['worklogs']
    time_spent_seconds = 0
    for each_work_log in work_logs:
        worklog_start = each_work_log['started']
        worklog_start_obj = datetime.strptime(worklog_start, "%Y-%m-%dT%X.%f%z")
        if worklog_start_obj > pre_week_start:
            time_spent_seconds = time_spent_seconds + each_work_log['timeSpentSeconds']
            output.append(each_work_log)
    total_time_spent = timedelta(seconds=time_spent_seconds)
    return {"workLogs": output, "timeSpent": total_time_spent}


if __name__ == "__main__":
    start_time = datetime.now()
    sample_url = "https://<domain>/rest/api/content/12345?expand=body.storage"
    page_id = "1187089322"
    page_url = f"{confluence_url}pages/viewpage.action?pageId={page_id}"
    get_page_body = f"{confluence_url}rest/api/content/{page_id}?expand=body.storage"
    r = requests.get(get_page_body, auth=(username, password))
    target_text = r.text.replace("</strong>", "").replace("<span>", "").replace("</span>", "")
    output = re.compile(r"2021_IR\S+\)").findall(target_text)

    i = 0
    start_week = ""
    if args.second_week:
        start_week = "-1w"
    jira_query_url = f"{jira_url}rest/api/2/search"
    jql_query = {
        "jql": f"worklogDate > startOfWeek({start_week}) AND worklogAuthor = allessunjoo.park"}
    r2 = requests.post(jira_query_url, auth=(username, password),
                       json=jql_query)
    a = json.loads(r2.text)
    total_work_logs = timedelta(seconds=0)
    total_work_logs_this_week = timedelta(seconds=0)
    sprint_time_delta = timedelta(hours=4)
    total_sp_0 = 0
    total_sp_planned = 0
    total_work_logs_unplanned = timedelta(seconds=0)
    output_table = []
    output_table_header = ['Sprint', 'Epic', '담당자', '진행 Backlog 회고', 'Worklogs', '결과 SP / 계획 SP', 'Time Spent',
                           '차기 Backlog', '계획 SP']
    # output_table.append(['Sprint', 'Key', 'SP', 'Time Spent', 'Summary', 'Worklogs'])
    if 'issues' in a.keys():
        for each_issue in a['issues']:
            issue_key = each_issue['key']
            issue_link = get_hlm_jira_link(issue_key)
            issue_summary = each_issue['fields']['summary']
            issue_fields = each_issue['fields']
            # Sprint field : code 10005
            # Story Point field : code 10002 
            # Epic field : code 10434
            # Get sprint info
            sprint_fields = issue_fields['customfield_10005']
            sp_planned = issue_fields['customfield_10002']
            if not sp_planned:
                sp_planned = 0
            total_sp_planned = total_sp_planned + int(sp_planned)
            # Get Epic Info
            epic_key = issue_fields['customfield_10434']
            epic_info = get_issue_info(jira_url, username, password, epic_key)
            epic_summary = epic_info['fields']['summary']
            epic_link = get_hlm_jira_link(epic_key)
            all_sprints = []
            active_sprint_name = ""
            # Detect 'ACTIVE' sprint
            for each_sprint_str in sprint_fields:
                # each_sprint_str
                #   - Example: com.atlassian.greenhopper.service.sprint.Sprint@690985ae[id=10076,rapidViewId=3198,state=ACTIVE,name=2021_IR2SP13(3/1-3/12),startDate=2021-03-02T10:00:01.420+09:00,endDate=2021-03-15T10:00:00.000+09:00,completeDate=<null>,sequence=10076,goal=<null>]
                sprint_data = re.compile(r"\[(\S+)\]").findall(each_sprint_str)[0]
                sprint_name = re.compile(r"name=(\S+),startDate=").findall(sprint_data)[0]
                sprint_status = re.compile(r"state=(\S+),name=").findall(sprint_data)[0]
                all_sprints.append(sprint_name)
                if sprint_status == "ACTIVE":
                    active_sprint_name = sprint_name
            work_logs = get_work_logs_from_previous_week(jira_url, username, password, issue_key)
            work_logs_time_spent = work_logs['timeSpent']
            total_work_logs = work_logs_time_spent + total_work_logs
            if sp_planned == 0:
                total_work_logs_unplanned = total_work_logs_unplanned + work_logs_time_spent
            story_point = work_logs_time_spent / sprint_time_delta
            total_sp_0 = total_sp_0 + story_point
            print("")
            print(active_sprint_name, issue_key, story_point, work_logs['timeSpent'], issue_summary)
            work_logs_messages = ""
            for each_work_log in work_logs['workLogs']:
                work_log_start = datetime.strptime(each_work_log['started'], "%Y-%m-%dT%X.%f%z")
                work_logs_time_spent = each_work_log['timeSpent']
                work_logs_time_spent_in_seconds = each_work_log['timeSpentSeconds']
                if work_log_start >= curr_week_start:
                    total_work_logs_this_week = total_work_logs_this_week + timedelta(
                        seconds=work_logs_time_spent_in_seconds)
                work_log_comment = each_work_log['comment']
                print("\n" + str(work_log_start) + f", {work_logs_time_spent}" + "\n" + work_log_comment)
                work_logs_messages = work_logs_messages + "\n" + str(
                    work_log_start) + f", {work_logs_time_spent}" + "\n" + work_log_comment
                work_logs_messages = work_logs_messages.replace("\n", "<br/>")
                work_logs_messages = work_logs_messages.replace("\r", "")
            account_id = get_confluence_user_info(confluence_url, username, password)['userKey']
            user_link = f"<ac:link><ri:user ri:userkey=\"{account_id}\"/></ac:link>"
            output_table.append(
                [active_sprint_name, epic_link, user_link, issue_link, work_logs_messages,
                 f"{story_point}/{sp_planned}", work_logs['timeSpent'], '', ''])
    df = pd.DataFrame(data=output_table, columns=output_table_header)
    html = df.to_html(escape=False)
    total_sp = total_work_logs / sprint_time_delta
    total_sp_this_week = total_work_logs_this_week / sprint_time_delta
    print(f"Total Story points: {total_sp}, Planned: {total_sp_planned}")
    html_prefix = f"<br/><pre> Total Story points: {total_sp}</pre>"
    html_prefix = html_prefix + f"<pre> Total Story points on this week: {total_sp_this_week}</pre>"
    html_prefix = html_prefix + f"<pre> Total Story points (unplanned): {total_work_logs_unplanned / sprint_time_delta}</pre>"
    html_prefix = html_prefix + f"<pre> Planned Story Points: {total_sp_planned}</pre><br/>"
    html = html_prefix + html
    output_path = os.environ['HOME'] + "/output.html"
    f = open(output_path, "w")
    f.write(html)

    parent_page_id = args.parent_page_id
    confluence_api_url = f"{confluence_url}rest/api/content/"
    confluence_space_key = args.confluence_space_key

    # Set Personal report page's title
    personal_page_title = f"Sprint report - {username}"

    # Find a page info with title
    find_page_url = f"{confluence_api_url}?type=page&spaceKey={confluence_space_key}&title={quote(personal_page_title)}"
    find_page = requests.get(find_page_url, auth=(username, password))
    find_page_result = json.loads(find_page.text)
    if len(find_page_result['results']) == 0:
        # If personal_page_title doesn't exit, create it
        personal_sprint_page_data = {
            "type": "page",
            "title": f"Sprint report - {username}",
            "ancestors": [{"id": parent_page_id}],
            "space": {"key": confluence_space_key},
            "body": {
                "storage": {
                    "value": "Personal Sprint Report Page",
                    "representation": "storage"
                }
            }
        }

        create_personal_report_page = requests.post(confluence_api_url, auth=(username, password),
                                                    json=personal_sprint_page_data)
        personal_page_id = json.loads(create_personal_report_page.text)['id']
    else:
        # Get existing page's id
        personal_page_id = find_page_result['results'][0]['id']

    # Create each sprint's report page
    sprint_page_data = {
        "type": "page",
        "title": f"Sprint report {str(today)}",
        "ancestors": [{"id": personal_page_id}],
        "space": {"key": confluence_space_key},
        "body": {
            "storage": {
                "value": html,
                "representation": "storage"
            }
        }
    }
    create_sp_report = requests.post(confluence_api_url, auth=(username, password), json=sprint_page_data)
    print(create_sp_report.status_code)
    create_sp_report_obj = json.loads(create_sp_report.text)
    # print a created page url
    page_url = f"{create_sp_report_obj['_links']['base'] + create_sp_report_obj['_links']['webui']}"
    print(page_url)
    end_time = datetime.now()
    print(end_time - start_time)
