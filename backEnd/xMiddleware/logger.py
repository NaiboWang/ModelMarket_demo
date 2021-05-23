import datetime
import json
import logging
import threading
import socket
from bson import json_util
from backEnd.dbconfig import *

from django.utils.deprecation import MiddlewareMixin

local = threading.local()

def beijing(sec, what):
    beijing_time = datetime.datetime.now() + datetime.timedelta(hours=8)
    return beijing_time.timetuple()


logging.Formatter.converter = beijing

class RequestLogFilter(logging.Filter):
    """
    日志过滤器
    """

    def filter(self, record):
        record.sip = getattr(local, 'sip', 'none')
        record.dip = getattr(local, 'dip', 'none')
        record.body = getattr(local, 'body', 'none')
        record.path = getattr(local, 'path', 'none')
        record.method = getattr(local, 'method', 'none')
        record.username = getattr(local, 'username', 'none')
        record.role = getattr(local, 'role', 'none')
        record.nickname = getattr(local, 'nickname', 'none')
        record.status_code = getattr(local, 'status_code', 'none')
        record.response = getattr(local, 'response', 'none')
        record.reason_phrase = getattr(local, 'reason_phrase', 'none')

        return True


class RequestLogMiddleware(MiddlewareMixin):
    """
    将request的信息记录在当前的请求线程上。
    """

    def __init__(self, get_response=None):
        self.get_response = get_response
        self.apiLogger = logging.getLogger('web.log')

    def __call__(self, request):
        response = self.get_response(request)
        if hasattr(response,'no_log'):
            return response
        try:
            body = json.loads(request.body)
        except Exception:
            body = dict()

        if request.method == 'GET':
            body.update(dict(request.GET))
        else:
            body.update(dict(request.POST))

        local.body = body
        local.path = request.path
        local.method = request.method
        if "username" in request.session:
            local.username = request.session["username"]
        else:
            local.username = "Guest"
        if "role" in request.session:
            local.role = request.session["role"]
        else:
            local.role = "Guest"
        if "nickname" in request.session:
            local.nickname = request.session["nickname"]
        else:
            local.nickname = "Guest"

        local.sip = request.META.get('REMOTE_ADDR', '')
        local.dip = socket.gethostbyname(socket.gethostname())

        local.response = json.loads(bytes.decode(response.content))
        if response.status_code != 200:
            local.response = ""
        local.status_code = response.status_code
        local.reason_phrase = response.reason_phrase
        self.apiLogger.info('system-auto')
        logs.insert_one(local.__dict__)
        return response