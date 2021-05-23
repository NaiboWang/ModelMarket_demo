from tzlocal import get_localzone
from datetime import datetime, timezone, timedelta
import time
from base64 import b64decode, b16decode
from django.conf import settings


def utc_now():
    utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)
    obj = utc_now.astimezone(timezone(timedelta(hours=8)))
    obj = datetime(obj.year, obj.month, obj.day, obj.hour, obj.minute, obj.second, obj.microsecond)
    return obj


def get_time_int():
    return str(int(round(time.time() * 1000)))


def decrypt_message(message):
    decode_data = b64decode(message)
    if len(decode_data) == 127:
        hex_fixed = '00' + decode_data.hex()
        decode_data = b16decode(hex_fixed.upper())
    return bytes.decode(settings.CIPHER.decrypt(decode_data, "ERROR"))
