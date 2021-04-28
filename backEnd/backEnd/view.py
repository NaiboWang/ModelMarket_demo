"""
User info management (login, register, check_login, etc)
"""

from django.http import HttpResponse
import json
from functools import wraps
from .dbconfig import *
from bson import json_util

from .tools import utc_now


def json_wrap(res):
    return HttpResponse(json.dumps(res, default=json_util.default), content_type="application/json")


def hello(request):
    return HttpResponse("Hello world!")


def check_login(f):
    @wraps(f)
    def inner(request, *arg, **kwargs):
        if request.session.get('is_login') == '1':
            return f(request, *arg, **kwargs)
        else:
            return HttpResponse(json.dumps({"status": 302, "msg": "Not logged in!"}),
                                content_type="application/json")

    return inner


def check_manager(f):
    @wraps(f)
    def inner(request, *arg, **kwargs):
        if request.session.get('role') == 'manager':
            return f(request, *arg, **kwargs)
        else:
            return HttpResponse(json.dumps({"status": 302, "msg": "Sorry, you don't have permission to do this!"}),
                                content_type="application/json")

    return inner


# 查找参数是否在请求中
def check_parameters(paras):
    def _check_parameter(f):
        @wraps(f)
        def inner(request, *arg, **kwargs):
            for para in paras:
                if para in request.GET or para in request.POST:
                    continue
                else:
                    return HttpResponse(
                        json.dumps({"status": 400, "msg": "Not specify required parameters: " + para + "!"}),
                        content_type="application/json")
            return f(request, *arg, **kwargs)

        return inner

    return _check_parameter


def getIdentity(request):
    if request.session.get('is_login') == '1':
        return HttpResponse(
            json.dumps({"status": 200, "role": request.session["role"], "username": request.session["username"]}),
            content_type="application/json")
    else:
        return HttpResponse(
            json.dumps({"status": 200, "role": "guest", "username": "guest"}),
            content_type="application/json")


@check_login
def getUserInfo(request):
    result = myauths.find({"username": request.session['username']}, {"pswd": 0})
    return json_wrap({"status": 200, "data": list(result)[0]})


@check_parameters(["query", "pageNum", "pageSize", "fields", "sortProp", "order"])
def getUserList(request):
    if request.session.get('role') == 'manager':
        result, total = queryTable(myauths, request, additionalColumns={"pswd": 0, "_id": 0})
        return json_wrap({"status": 200, "data": list(result), "total": total})
    else:
        return HttpResponse(
            json.dumps({"status": 303, "msg": "Sorry, you don't have permission to check this list!"}),
            content_type="application/json")


@check_login
@check_parameters(["status", 'id'])
def changeUserStatus(request):
    res = myauths.find({"id": int(request.GET['id'])})
    r = list(res)
    if len(r) == 0:  # 没找到值
        result = {"status": 404, "msg": "User not found!"}
    elif r[0]["role"] == 'manager':
        result = {"status": 305, "msg": "Sorry, manager cannot be disabled!"}
    else:
        if request.GET["status"] == "true":
            status = True
        else:
            status = False
        myauths.update_one({"id": int(request.GET["id"])}, {'$set': {"status": status}})
        if status:
            msg = "Normal"
        else:
            msg = "Disabled"
        result = {"status": 200, "msg": "User status has been successfully set to " + msg}
    return HttpResponse(json.dumps(result), content_type="application/json")


@check_manager
@check_parameters(['id'])
def resetPassword(request):
    res = myauths.find({"id": int(request.GET['id'])})
    r = list(res)
    if len(r) == 0:  # 没找到值
        result = {"status": 404, "msg": "User not found!"}
    elif r[0]["role"] == 'manager':
        result = {"status": 305, "msg": "Sorry, manager's password cannot be reset!"}
    else:
        myauths.update_one({"id": int(request.GET["id"])}, {'$set': {"pswd": 'qq'}})
        result = {"status": 200, "msg": "User password has been successfully set to 'qq'"}
    return HttpResponse(json.dumps(result), content_type="application/json")


@check_login
def getUserDeposit(request, username=False):
    if username:
        result = list(myauths.find({"username": username}, {"deposit": 1}))
    else:
        result = list(myauths.find({"username": request.session["username"]}, {"deposit": 1}))
    if len(result) > 0:
        return result[0]["deposit"]
    else:
        return False


@check_login
def setUserDeposit(request, deposit=0, username=False):
    # 如果能查到用户存款
    if getUserDeposit(request, username):
        if username:
            myauths.update_one({"username": username}, {'$set': {"deposit": deposit}})
        else:
            myauths.update_one({"username": request.session["username"]}, {'$set': {"deposit": deposit}})


@check_parameters(["username", "pass"])
def login(request):
    result = myauths.find({"username": request.POST['username']})
    r = list(result)
    if len(r) == 0:  # 没找到值
        result = {"status": 404, "msg": "User not found!"}
    else:
        item = r[0]
        print(item["status"])
        if item["pswd"] != request.POST['pass']:
            result = {"status": 201, "msg": "Wrong password!"}
        elif not item["status"]:
            result = {"status": 202, "msg": "Sorry, this account has been disabled!"}
        else:
            result = {"status": 200, "role": item["role"],'msg':'Login Success!'}
            request.session['is_login'] = '1'
            request.session["username"] = request.POST["username"]
            request.session["role"] = item["role"]
            request.session.set_expiry(1200)
    return HttpResponse(json.dumps(result), content_type="application/json")


@check_login
def logout(request):
    request.session.flush()
    return HttpResponse(json.dumps({"status": 200, "msg": "Logout success!"}), content_type="application/json")


@check_login
def changePassword(request):
    result = myauths.find({"username": request.session["username"]})
    r = list(result)
    if r[0]["pswd"] == request.POST["oldPass"]:
        myauths.update_one({"username": request.session["username"]}, {'$set': {"pswd": request.POST['pass']}})
        logout(request)
        return HttpResponse(json.dumps({"status": 200}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({"status": 401, "msg": "Old password is not correct!"}),
                            content_type="application/json")


def register(request):
    result = myauths.find({"username": request.POST['username']})
    r = list(result)
    if len(r) == 0:  # 没找到值
        user = {"username": request.POST['username'], "pswd": request.POST['pass'], "role": "user", "deposit": 0,
                "status": True, "register_time": utc_now().strftime("%Y-%m-%d %H:%M:%S")}
        res = list(myauths.find({}).sort("id", -1).skip(0).limit(1))
        if len(res) == 0:
            user["id"] = 0
        else:
            user["id"] = int(res[0]["id"]) + 1
        myauths.insert_one(user)
        return HttpResponse(json.dumps({"status": 200, "msg": "Register Success, please log in!"}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({"status": 401, "msg": "User already exists!"}),
                            content_type="application/json")


@check_login
@check_parameters(["amount"])
def charge(request):
    deposit = getUserDeposit(request)
    deposit += int(request.GET["amount"])  # 平台抽走20%利润
    setUserDeposit(request, deposit)
    return json_wrap({"status": 200, })
