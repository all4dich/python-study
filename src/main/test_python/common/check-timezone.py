import time
from datetime import datetime
import pytz
from pytz import utc
import tzlocal

# https://spoqa.github.io/2019/02/15/python-timezone.html
local_tz = tzlocal.get_localzone()
tz_name = str(local_tz)

seoul_tz = pytz.timezone(tz_name)
seoul_date = datetime.now(seoul_tz)
seoul_tz_offset = seoul_date.strftime('%z')
# naive time object
utc_now = datetime.utcnow()
seoul_now = datetime.now()

print(utc_now)
print(seoul_now)
print("")
# aware time object
utc_now_utc = utc.localize(utc_now)
utc_now_kst = seoul_tz.localize(utc_now)
print(utc_now_utc)
print(utc_now_kst)
print("")
print(utc_now_utc.astimezone(seoul_tz))
print(utc_now_utc.astimezone(seoul_tz) - utc_now_kst)
print(utc_now_utc - utc_now_kst)
print("")
seoul_now_kst = seoul_tz.localize(seoul_now)
print(seoul_now_kst - utc_now_utc)
print(seoul_now_kst - utc_now_kst)
print(utc_now_utc - utc_now_kst)