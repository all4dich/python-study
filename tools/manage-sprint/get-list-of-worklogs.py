import requests
import argparse
import re
import json
from datetime import datetime, timedelta
import pandas as pd
import os

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("--username", required=True)
arg_parser.add_argument("--password", required=True)
arg_parser.add_argument("--second-week", action="store_true")
args = arg_parser.parse_args()
username = args.username
password = args.password

mlt4tv_sprints = "http://collab.lge.com/main/pages/viewpage.action?pageId=1187089322"

def get_issue_info(url, username, password, issue_key):
    get_issue_info_url = f"{url}rest/api/2/issue/{issue_key}"
    r = requests.get(get_issue_info_url, auth=(username, password))
    issue_info = json.loads(r.text)
    return issue_info

def get_work_logs_from_previous_week(url, username, password, issue_key):
    output = []
    #             get_issue_worklog_url = f"{self._api_root}issue/{each_issue['key']}/worklog"
    today = datetime.now().astimezone()
    local_tz = today.tzinfo
    # Current Week
    curr_week_start =  today - timedelta(days=today.weekday())
    # curr_week_end: Friday
    curr_week_end =  curr_week_start + timedelta(days=4)
    # Previous Week
    pre_week_start =  today - timedelta(weeks=1, days=today.weekday())
    # curr_week_end: Friday
    pre_week_end =  pre_week_start + timedelta(days=4)

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
    jira_url = "http://hlm.lge.com/issue/"
    jira_query_url = f"{jira_url}rest/api/2/search"
    jql_query = {
        "jql": f"worklogDate > startOfWeek({start_week}) AND worklogAuthor = allessunjoo.park"}
    r2 = requests.post(jira_query_url, auth=(username, password),
                       json=jql_query)
    a = json.loads(r2.text)
    total_times = timedelta(seconds=0)
    sprint_time_delta = timedelta(hours=4)
    total_sp_0 = 0
    total_sp_planned = 0
    total_spent_time_unplanned = timedelta(seconds=0)
    output_table = []
    output_table_header = ['Sprint', 'Epic', 'Key', 'SP', 'SP Planned', 'Time Spent', 'Summary', 'Worklogs']
    #output_table.append(['Sprint', 'Key', 'SP', 'Time Spent', 'Summary', 'Worklogs'])
    if 'issues' in a.keys():
        for each_issue in a['issues']:
            issue_key = each_issue['key']
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
            total_times = work_logs_time_spent + total_times
            if sp_planned == 0:
                total_spent_time_unplanned = total_spent_time_unplanned + work_logs_time_spent
            story_point = work_logs_time_spent / sprint_time_delta
            total_sp_0 = total_sp_0 + story_point
            print("")
            print(active_sprint_name, issue_key, story_point, work_logs['timeSpent'], issue_summary)
            work_logs_messages = ""
            for each_work_log in work_logs['workLogs']:
                work_log_start = datetime.strptime(each_work_log['started'], "%Y-%m-%dT%X.%f%z")
                work_logs_time_spent = each_work_log['timeSpent']
                work_log_comment = each_work_log['comment']
                print("\n" + str(work_log_start) + f", {work_logs_time_spent}" + "\n" + work_log_comment)
                work_logs_messages = work_logs_messages+ "\n" + str(work_log_start) + f", {work_logs_time_spent}" + "\n" + work_log_comment
                work_logs_messages = work_logs_messages.replace("\n", "<br/>")
                work_logs_messages = work_logs_messages.replace("\r", "")
            output_table.append([active_sprint_name, epic_summary, issue_key, story_point, sp_planned, work_logs['timeSpent'], issue_summary, work_logs_messages])
    df = pd.DataFrame(data=output_table, columns=output_table_header)
    html = df.to_html(escape=False)
    total_sp = total_times / sprint_time_delta
    print(f"Total Story points: {total_sp}, Planned: {total_sp_planned}")
    html = html + f"<br/><pre> Total Story points: {total_sp}, Planned: {total_sp_planned}</pre>"
    html = html + f"<pre> Total Story points ( unplanned ): {total_spent_time_unplanned/sprint_time_delta}</pre>"
    output_path = os.environ['HOME'] + "/output.html"
    f = open(output_path, "w")
    f.write(html)