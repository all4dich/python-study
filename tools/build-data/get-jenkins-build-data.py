import argparse
from datetime import datetime, timedelta
import tzlocal
import pytz
import pymongo
import pandas as pd
import numpy as np
import os
import re

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("--db-host", required=True, help="DB Host address")
arg_parser.add_argument("--db-port", help="DB Host port", default=27017)
arg_parser.add_argument("--db-name", required=True, help="DB Name")
arg_parser.add_argument("--auth-db-name", help="DB Name for authoring user information", default="admin")
arg_parser.add_argument("--db-user", required=True, help="DB Username")
arg_parser.add_argument("--db-password", required=True, help="DB Password")
arg_parser.add_argument("--db-collection", required=True, help="DB Password")
arg_parser.add_argument("--start-day", required=True, help="Start date for query. Use ISO Format like 2021-01-09")
arg_parser.add_argument("--end-day", help="End date for query. Use ISO Format like 2021-01-09")
arg_parser.add_argument("--tz-name",
                        help="Time zone's name to use --start-day / --end-day. You can check all time zone's name "
                             "from pytz.all_timezones", default=str(tzlocal.get_localzone()))
arg_parser.add_argument("--out-file", help="Excel file(*.xlsx) path to write results")

args = arg_parser.parse_args()

if __name__ == "__main__":
    db_host = args.db_host
    db_port = args.db_port
    db_name = args.db_name
    db_user = args.db_user
    db_password = args.db_password
    db_collection = args.db_collection
    start_day = args.start_day
    end_day = args.end_day
    tz_name = args.tz_name
    your_tz = pytz.timezone(tz_name)
    utc_tz = pytz.utc

    # Convert datetime string to datetime object
    start_date = your_tz.localize(datetime.fromisoformat(start_day))
    end_date = your_tz.localize(datetime.fromisoformat(end_day))
    start_epoch = start_date.timestamp()
    end_epoch = end_date.timestamp()

    # Prepare db conneciton
    connection = pymongo.MongoClient(f"mongodb://{db_user}:{db_password}@{db_host}:{db_port}/{args.auth_db_name}")
    database = connection.get_database(db_name)
    collection = database.get_collection(db_collection)

    db_query_statement = collection.find(
        {"$and": [
            {"start": {"$gt": start_epoch}},
            {"start": {"$lt": end_epoch}}
        ]})

    data_header = ["host", "year", "month", "day", "day_full_str", "hour", "jobname", "buildnumber", "branch_name",
                   "type",
                   "chip", "duration", "duration in seconds", "time_rm_build", "time_rm_build in seconds",
                   "time_rsync_artifacts", "time_rsync_artifacts in seconds", "time_build_sh",
                   "time_build_sh_in_seconds",
                   "duration_in_queue"]

    out_file_name = args.out_file
    if out_file_name is None:
        print("You didn't set --out-file arguments.")
    else:
        if os.path.exists(out_file_name):
            print(f"INFO: {out_file_name} exist.")
            file_name, file_ext = os.path.splitext(out_file_name)
            curr_date = str(datetime.now())
            out_file_name = f"{file_name}-{curr_date}{file_ext}"
    data_body = []
    i = 1
    for each_build in db_query_statement:
        job_name = each_build['jobname']
        host_name = each_build['host']
        build_number = each_build['buildnumber']
        duration_in_queue = each_build['duration_in_queue']
        chip_name = each_build['machine']
        job_name_split = job_name.split("-")
        branch_name = job_name_split[1]
        if branch_name == "engineering":
            branch_name = "clean"
        build_type = job_name_split[2]
        if build_type == "starfish" and re.compile(r"clean-.*").match(job_name):
            build_type = "clean"
        build_start = each_build["start"]
        build_start_date = datetime.fromtimestamp(build_start, your_tz)
        build_year = build_start_date.year
        build_month = build_start_date.month
        build_day = build_start_date.day
        build_hour = build_start_date.hour
        build_minute = build_start_date.minute
        time_build_sh = each_build["time_build_sh"]
        time_build_sh_min = timedelta(seconds=time_build_sh)
        time_rm_build = each_build["time_rm_build"]
        time_rm_build_min = timedelta(seconds=time_rm_build)
        time_rsync_artifacts = each_build["time_rsync_artifacts"]
        time_rsync_artifacts_min = timedelta(seconds=time_rsync_artifacts)
        duration = each_build["duration"]
        duration_min = timedelta(seconds=duration)
        day_full_str = f"2020/{build_month}/{build_day}"
        if not re.compile(r".*(soyul|sunjoo|clean).*").match(branch_name):
            i = i + 1
            data_body.append(
                [host_name, build_year, build_month, build_day, day_full_str, build_hour, job_name, build_number,
                 branch_name, build_type, chip_name, duration_min, duration, time_rm_build_min, time_rm_build,
                 time_rsync_artifacts_min, time_rsync_artifacts, time_build_sh_min, time_build_sh, duration_in_queue])
    df = pd.DataFrame(data_body, columns=data_header)
    print(i)
    table_chip_build_count = pd.pivot_table(
        df, values='host', index=['year', 'month', 'chip'], aggfunc="count", fill_value=0, margins=True)
    table_chip_build_count_2 = pd.pivot_table(
        df, values='host', index=['year', 'month'], columns=['chip'], aggfunc=np.any)
    table_branch_build_count = pd.pivot_table(
        df, values='host', index=['year', 'month', 'branch_name'], columns=['type'], aggfunc="count", fill_value=0,
        margins=True)
    print(out_file_name)
    if out_file_name is None:
        print(df)
    else:
        print("INFO: Create a file = " + out_file_name)
        with pd.ExcelWriter(out_file_name) as writer:
            # df.to_excel(excel_writer=writer, sheet_name="Raw data")
            table_chip_build_count.to_excel(excel_writer=writer, sheet_name="Chip Build Count")
            table_chip_build_count_2.to_excel(excel_writer=writer, sheet_name="Chip Build Count 2")
            table_branch_build_count.to_excel(excel_writer=writer, sheet_name="Branch Build Count")
    print("Done:")
