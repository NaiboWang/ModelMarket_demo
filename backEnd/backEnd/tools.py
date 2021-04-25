from tzlocal import get_localzone
from datetime import datetime, timezone, timedelta
import time


def utc_now():
    utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)
    obj = utc_now.astimezone(timezone(timedelta(hours=8)))
    obj = datetime(obj.year, obj.month, obj.day, obj.hour, obj.minute, obj.second, obj.microsecond)
    return obj


def get_time_int():
    return str(int(round(time.time() * 1000)))
