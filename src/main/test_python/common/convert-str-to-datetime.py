from datetime import datetime, timedelta, timezone, time, date
import pytz

month = str(1)
day = str(2)
start_str = f"2020-{month.zfill(2)}-{day.zfill(2)}"

# Link: https://docs.python.org/3/library/datetime.html#datetime.date.fromisoformat
# isoformat example: YYYY-MM-DD
start_date = datetime.fromisoformat(start_str).astimezone()

# Get a city's time zone info: Use pytz
seoul_tz = pytz.timezone("Asia/Seoul")
# Get Local TZ: Use .astimezone().tzinfo
local_tz = datetime.now().astimezone().tzinfo
# Get a time zone with timedelta
your_tz = timezone(timedelta(hours=0))

print(f"Local tz: {local_tz}")
start_epoch = start_date.timestamp()
print(start_date)
print(start_epoch)
print("")
# Create UTC datetime with that date string in UTC
start_date_in_utc = datetime(year=2020, month=int(month), day=int(day), tzinfo=pytz.utc)
print(start_date_in_utc)
# Get local time datetime object with defined date string in the local
start_date_in_local = datetime(year=2020, month=int(month), day=int(day), tzinfo=local_tz)
print(start_date_in_local)

date_utc = datetime.utcfromtimestamp(start_epoch).replace(tzinfo=your_tz)
print(date_utc.timestamp())
print("")
today = datetime.today()
print(today)