"""
User info management (login, register, check_login, etc)
"""

from django.http import HttpResponse
import json
from functools import wraps
from .dbconfig import *


def hello(request):
    return HttpResponse("Hello world!")


def check_login(f):
    @wraps(f)
    def inner(request, *arg, **kwargs):
        if request.session.get('is_login') == '1':
            return f(request, *arg, **kwargs)
        else:
            return HttpResponse(json.dumps({"status": 301, "reason": "Not logged in!"}), content_type="application/json")
    return inner


@check_login
def getIdentity(request):
    return HttpResponse(
        json.dumps({"status": 200, "role": request.session["role"], "username": request.session["username"]}),
        content_type="application/json")


def login(request):
    result = myauths.find({"username": request.POST['username']})
    r = list(result)
    if len(r) == 0:  # 没找到值
        result = {"status": 404, "reason": "User not found!"}
        print("User not found")
    else:
        item = r[0]
        if item["pswd"] != request.POST['pass']:
            result = {"status": 201, "reason": "Wrong password!"}
        else:
            result = {"status": 200, "role": item["role"]}
            request.session['is_login'] = '1'
            request.session["username"] = request.POST["username"]
            request.session["role"] = item["role"]
            request.session.set_expiry(1200)
    return HttpResponse(json.dumps(result), content_type="application/json")


@check_login
def logout(request):
    request.session.flush()
    return HttpResponse(json.dumps({"status": 200, }), content_type="application/json")


def register(request):
    result = myauths.find({"username": request.POST['username']})
    r = list(result)
    if len(r) == 0:  # 没找到值
        user = {"username": request.POST['username'], "pswd": request.POST['pass'], "role": "user"}
        myauths.insert_one(user)
        return HttpResponse(json.dumps({"status": 200}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({"status": 302, "reason": "User already exists!"}),
                            content_type="application/json")
