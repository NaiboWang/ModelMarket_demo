"""
Order Management
"""

from django.http import HttpResponse
import json
import os, time
from bson import json_util
from django.http import FileResponse
from .dbconfig import *
from functools import wraps
from .modelMangement import check_id
from .view import check_login, check_parameters, json_wrap, getUserDeposit, setUserDeposit


@check_login
@check_id
def buyModel(request, result=""):
    deposit = getUserDeposit(request)
    if deposit < result["price"]:
        return HttpResponse(
            json.dumps({"status": 350, "msg": "Sorry, your deposit is not enough to pay!"}),
            content_type="application/json")
    else:
        deposit -= result["price"]
        setUserDeposit(request, deposit)
        author_deposit = getUserDeposit(request, result["author"])
        author_deposit += result["price"] * 0.8 # 平台抽走20%利润
        manager_deposit = getUserDeposit(request, "admin")
        manager_deposit += result["price"] - result["price"] * 0.8
        setUserDeposit(request, manager_deposit, "admin")
        setUserDeposit(request, author_deposit,result["author"])
    del result["_id"]
    result["purchase_time"] = time.strftime("%Y-%m-%d-%H-%M-%S.", time.localtime())
    result["buyer"] = request.session["username"]
    res = list(orders.find({}).sort("id", -1).skip(0).limit(1))
    if len(res) == 0:
        result["id"] = 0
    else:
        result["id"] = int(res[0]["id"]) + 1
    orders.insert_one(result)

    return HttpResponse(
        json.dumps({"status": 200, "msg": "Purchase successfully!"}), content_type="application/json")
