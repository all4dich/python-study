import requests
import argparse
from datetime import datetime, timedelta, timezone, tzinfo
import tzlocal
import pytz
import pymongo

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

    i = 1
    for each_build in db_query_statement:
        print(i)
        i = i + 1
