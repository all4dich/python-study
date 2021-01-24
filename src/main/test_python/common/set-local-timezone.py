import time
from datetime import datetime, timedelta, timezone, time
import pytz
from pytz import utc
import tzlocal
import sys

# https://spoqa.github.io/2019/02/15/python-timezone.html
#local_tz = tzlocal.get_localzone()
local_tz = datetime.now().astimezone().tzinfo
print(datetime.now().tzinfo)
tz_name = str(local_tz)

#seoul_tz = pytz.timezone(tz_name)
seoul_tz = local_tz
#seoul_date = datetime.now(seoul_tz)
seoul_date = datetime.now().astimezone()
#ad = timezone(timedelta(hours=9))
utc_now = datetime.utcnow()
local_now = datetime.now()
KST = timezone(timedelta(hours=9))
UTC = timezone(timedelta(hours=0))
print(local_now)
print(seoul_date)
seoul_date_2 = datetime.now(UTC)
seoul_date_3 = datetime.now(local_tz)
seoul_date_4 = datetime.now().astimezone(UTC)
print(seoul_date_2)
print(seoul_date_3)
print(seoul_date_3 - seoul_date_2)
print(seoul_date_4 - seoul_date_2)
sys.exit()
print(type(seoul_tz))
print(type(local_tz))
print(type(KST))
print("# Before astimezone")
print("utc now : " + str(utc_now))
print("local now : " + str(local_now))
print("# After astimezone")
print("utc now : " + str(utc_now.astimezone(UTC)))
print("local now:" + str(local_now.astimezone(KST)))
print("# After astimezone")
utc_now_2 = utc_now.astimezone(UTC)
utc_now_3 = utc_now_2.astimezone(KST)
print(utc_now_2)
print(utc_now_3 == utc_now_2)
print("# Chjeck local object")
print(local_now)
local_now_tz = local_now.astimezone()
print(local_now_tz)
print(seoul_tz.localize(local_now))
