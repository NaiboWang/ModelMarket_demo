"""
Order Management
"""
import random

from django.http import HttpResponse
import json
import os, time
from bson import json_util
from django.http import FileResponse
from .dbconfig import *
from functools import wraps
from .modelMangement import check_id
from .tools import utc_now, get_time_int, json_wrap
from .view import check_login, check_parameters, getUserDeposit, setUserDeposit


aggregationNicknameCondition = [
    {'$lookup': {'from': "auths", "localField": "author", "foreignField": "username", "as": "author_info"}},
    {'$unwind': {'path': '$author_info', 'preserveNullAndEmptyArrays': True}},
    {'$addFields': {'nickname': "$author_info.nickname"}},
    {'$lookup': {'from': "auths", "localField": "buyer", "foreignField": "username", "as": "author_info2"}},
    {'$unwind': {'path': '$author_info2', 'preserveNullAndEmptyArrays': True}},
    {'$addFields': {'nickname_buyer': "$author_info2.nickname"}},
    {'$project': {'author_info': 0,'author_info2': 0, '_id':0}}]


def getNewConditionBaseOnNickname(condition):
    qc = aggregationNicknameCondition.copy()
    qc.append({"$match": condition})
    return qc

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
        author_deposit += result["price"] * 0.8  # 平台抽走20%利润
        manager_deposit = getUserDeposit(request, "admin")
        manager_deposit += result["price"] - result["price"] * 0.8
        result["income_author"] = result["price"] * 0.8
        result["income_manager"] = result["price"] - result["price"] * 0.8
        setUserDeposit(request, manager_deposit, "admin")
        setUserDeposit(request, author_deposit, result["author"])
    if "_id" in result:
        del result["_id"]
    result["purchased_time"] = utc_now().strftime("%Y-%m-%d %H:%M:%S")
    result["buyer"] = request.session["username"]
    res = list(orders.find({}).sort("id", -1).skip(0).limit(1))
    order_id = str(result["id"]) + utc_now().strftime("%Y%m%d%H%M%S")
    if len(res) == 0:
        result["id"] = 0
    else:
        result["id"] = int(res[0]["id"]) + 1
    order_id += str(result["id"])
    result["orderID"] = order_id
    orders.insert_one(result)

    return HttpResponse(
        json.dumps({"status": 200, "msg": "Purchase successfully!"}), content_type="application/json")


@check_login
@check_parameters(["query", "pageNum", "pageSize", "fields", "sortProp", "order"])
def queryPurchasedOrders(request):
    if request.session["role"] == "manager":
        result, total = queryTable(orders, request, aggregationConditions=aggregationNicknameCondition)
        return json_wrap({"status": 200, "data": result, "total": total}, no_response=True)
    else:
        result, total = queryTable(orders, request, additionalConditions=[{"buyer": request.session["username"]}], aggregationConditions=aggregationNicknameCondition)
        return json_wrap({"status": 200, "data": result, "total": total}, no_response=True)

@check_login
@check_parameters(["query", "pageNum", "pageSize", "fields", "sortProp", "order"])
def querySoldOrders(request):
    if request.session["role"] == "manager":
        result, total = queryTable(orders, request, aggregationConditions=aggregationNicknameCondition)
        return json_wrap({"status": 200, "data": result, "total": total}, no_response=True)
    else:
        result, total = queryTable(orders, request, additionalConditions=[{"author": request.session["username"]}],  aggregationConditions=aggregationNicknameCondition)
        return json_wrap({"status": 200, "data": result, "total": total}, no_response=True)

@check_login
@check_parameters(["id"])
def queryOrder(request):
    result = list(orders.aggregate(getNewConditionBaseOnNickname({"id": int(request.GET["id"])})))
    if len(result) == 0:
        return HttpResponse(
            json.dumps({"status": 404, "msg": "We can't find order info based on given ID!"}),
            content_type="application/json")
    if result[0]["author"] == request.session["username"] or request.session["role"] == "manager":
        return json_wrap({"status": 200, "data": result[0]}, no_response=True)
    elif result[0]["buyer"] == request.session["username"]:
        result = list(orders.find({"id": int(request.GET["id"])},{"income_author":0,"income_manager":0}))
        return json_wrap({"status": 200, "data": result[0]}, no_response=True)
    else:
        return json_wrap({"status": 503, "msg": "Sorry, you don't have the permission to see this information!"})
