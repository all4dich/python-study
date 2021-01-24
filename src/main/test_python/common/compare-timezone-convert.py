from datetime import datetime, timedelta, timezone, time

# check tzlocal

curr_date = datetime.now()
local_date = curr_date.astimezone()
print(curr_date)
print(local_date)
print(local_date.tzinfo)

import pytz
# Some countries has multiple time zones`
# Create time zone from pytz. time zone name
tz_name = pytz.country_timezones["KR"][0]
us_pacific_zone = pytz.timezone("US/Pacific")
utc_zone = pytz.timezone("UTC")
seoul_zone = pytz.timezone(tz_name)
us_date = local_date.astimezone(us_pacific_zone)
print(us_date)
seoul_date = local_date.astimezone(seoul_zone)
print(seoul_date)
utc_date = local_date.astimezone(utc_zone)
print(utc_date)

# Check utctimestamp
print("")
stamp_val = 1611504975
date_local = datetime.fromtimestamp(stamp_val).astimezone()
date_utc = datetime.utcfromtimestamp(stamp_val).replace(tzinfo=utc_zone)
print(date_local - date_utc)

