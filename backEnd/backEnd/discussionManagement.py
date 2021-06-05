"""
Discussion Management
"""
import random

from django.http import HttpResponse
import json
import os, time
from bson import json_util, ObjectId
from django.http import FileResponse
from .dbconfig import *
from functools import wraps
from .modelMangement import check_id
from .tools import utc_now, get_time_int, json_wrap
from .view import check_login, check_parameters, getUserDeposit, setUserDeposit

aggregationNicknameConditions = [
    {'$unwind': {'path': '$discussion_list', 'preserveNullAndEmptyArrays': True}},  # 展开discussion_list数组
    {'$lookup': {'from': "auths", "localField": "discussion_list.speaker", "foreignField": "username",
                 "as": "author_info"}},  # 外键连接
    {'$unwind': {'path': '$author_info', 'preserveNullAndEmptyArrays': True}},  # 展开连接的外键
    {'$addFields': {'nickname': "$author_info.nickname"}},  # 增加字段
    {'$project': {'discussion_list': 1, "nickname": 1, 'modelID': 1, 'title': 1}}]  # 取指定字段


def getNewConditionBaseOnNickname(condition):
    qc = aggregationNicknameConditions.copy()
    qc.append({"$match": condition})
    return qc


@check_parameters(["queryFields", "pageNum", "pageSize", "fields", "sortProp", "order"])
def queryDiscussions(request):
    aggregationNicknameCondition = [
        {'$lookup': {'from': "auths", "localField": "author", "foreignField": "username", "as": "author_info"}},
        {'$unwind': {'path': '$author_info', 'preserveNullAndEmptyArrays': True}},
        {'$addFields': {'nickname': "$author_info.nickname"}},
        {'$project': {'author_info': 0, 'discussion_list': 0}}]
    ac = json.loads(request.POST["additionalConditions"])
    ac['modelID'] = int(ac['modelID'])
    result, total = queryTable(discussions, request, aggregationConditions=aggregationNicknameCondition,
                               additionalConditions=[ac])
    return json_wrap({"status": 200, "data": result, "total": total}, no_response=True)


@check_parameters(["id"])
def queryDiscussion(request):
    result = list(discussions.aggregate(getNewConditionBaseOnNickname({'_id': ObjectId(request.GET["id"])})))
    if len(result) == 0:
        return HttpResponse(
            json.dumps({"status": 404, "msg": "We can't find discussion info based on given ID!"}),
            content_type="application/json")
    return json_wrap({"status": 200, "data": result}, no_response=True)


@check_login
@check_parameters(["content", 'id'])
def addReply(request):
    ids = ObjectId(request.POST["id"])
    res = discussions.find_one({'_id': ids})
    r = list(res)
    if len(r) == 0:  # 没找到值
        result = {"status": 404, "msg": "Info not found!"}
    else:
        ut = utc_now().strftime("%Y-%m-%d %H:%M:%S")
        result = pushToList(request, ids, request.POST['content'], ut)
    return HttpResponse(json.dumps(result), content_type="application/json")


def pushToList(request, ids, content, ut):
    info = {
        'speaker': request.session["username"],
        'time': ut,
        'content': content,
    }
    discussions.update_one({"_id": ids}, {'$addToSet': {"discussion_list": info}, '$set': {'update_time': ut}})
    result = list(models.find({"id": int(request.POST["modelID"])}))[0]
    if request.session["username"] != result["author"]:
        message = request.session["nickname"] + " commented on Discussion " + request.POST['title'] + " at " + ut
        notifications.insert_one(
            {"username": result["author"], "read": 0, "discussionID": str(ids), "message": message, "time": ut})
    result = {"status": 200, "msg": "Reply Successfully"}
    return result


@check_login
@check_parameters(["content", 'title', 'modelID'])
def addTopic(request):
    info = dict()
    info['title'] = request.POST['title']
    info['modelID'] = int(request.POST['modelID'])
    ut = utc_now().strftime("%Y-%m-%d %H:%M:%S")
    info["create_time"] = ut
    info["update_time"] = ut
    info["author"] = request.session["username"]
    info["discussion_list"] = []
    r = discussions.insert_one(info)
    pushToList(request, r.inserted_id, request.POST['content'], ut)
    return json_wrap({"status": 200, "msg": "Add topic successfully", 'id': str(r.inserted_id)})

@check_login
@check_parameters(["pageNum"])
def queryNotifications(request):
    query = notifications.find({"username": request.session["username"]})
    sortCondition = [("time", -1)]
    query.sort(sortCondition).skip(10 * (int(request.GET['pageNum']) - 1)).limit(10).collation({"locale": "en"})
    result = list(query)
    total = query.count()
    return json_wrap({"status": 200, "data": result, "total": total}, no_response=True)