"""
Model Management
"""

import json
import os
from functools import wraps

from bson import json_util
from django.http import FileResponse
from django.http import HttpResponse
from .netdrawer import main as getDot
from .dbconfig import *
from .tools import utc_now
from .view import check_login, check_parameters, json_wrap


# 检查Id对应模型是否存在
def check_id(f):
    @wraps(f)
    def inner(request, *arg, **kwargs):
        if 'id' in request.GET:
            tid = request.GET['id']
            try:
                res = list(models.find({"id": int(tid)}, {"_id": 0}))
                if len(res) > 0:
                    return f(request, res[0], *arg, **kwargs)
                else:
                    return HttpResponse(
                        json.dumps({"status": 404, "msg": "We can't find model infos based on given ID!"}),
                        content_type="application/json")
            except:
                return HttpResponse(
                    json.dumps({"status": 404, "msg": "We can't find model infos based on given ID!"}),
                    content_type="application/json")
        else:
            return HttpResponse(json.dumps({"status": 400, "msg": "Please specify the model ID!"}),
                                content_type="application/json")

    return inner


# 检查Id对应模型的用户是否有权限操作模型
def check_idAuth(f):
    @wraps(f)
    def inner(request, result, *arg, **kwargs):
        if result['author'] == request.session["username"] or request.session["role"] == "manager":
            return f(request, result, *arg, **kwargs)
        else:
            return HttpResponse(
                json.dumps({"status": 501, "msg": "Sorry, you don't have the permission to do this!"}),
                content_type="application/json")

    return inner


@check_id
def queryModel(request, result):
    return HttpResponse(json.dumps({"status": 200, "data": result}, default=json_util.default),
                        content_type="application/json")


@check_parameters(["query", "pageNum", "pageSize", "fields", "sortProp", "order"])
def queryModels(request):
    result, total = queryTable(models, request, additionalConditions=[{"status": True}])
    return json_wrap({"status": 200, "data": result, "total": total})


@check_login
@check_parameters(["query", "pageNum", "pageSize", "fields", "sortProp", "order"])
def queryModelsManagement(request):
    if request.session["role"] == "manager":
        result, total = queryTable(models, request)
        return json_wrap({"status": 200, "data": result, "total": total})
    else:
        result, total = queryTable(models, request, additionalConditions=[{"author": request.session["username"]}])
        return json_wrap({"status": 200, "data": result, "total": total})


@check_login
def manageModel(request):
    data = request.POST['params']
    data = json.loads(data)
    data["author"] = request.session["username"]
    t = utc_now().strftime("%Y-%m-%d %H:%M:%S")
    if int(data["id"]) == -1:
        result = list(models.find({}).sort("id", -1).skip(0).limit(1))
        if len(result) == 0:
            data["id"] = 0
        else:
            data["id"] = int(result[0]["id"]) + 1  # 修改id
        data["created_time"] = t
        data["updated_time"] = t
        models.insert_one(data)
    else:
        result = list(models.find({"id": int(data["id"])}))[0]
        if result['author'] == request.session["username"]:
            models.delete_one({"id": int(data["id"])})
            data["updated_time"] = t
            models.insert_one(data)
            return HttpResponse(json.dumps({"status": 200}), content_type="application/json")
        else:
            return HttpResponse(json.dumps({"status": 400, "msg": "Not correct user, permission denied."}),
                                content_type="application/json")
    return HttpResponse(
        json.dumps({"status": 200, "id": int(data["id"])}), content_type="application/json")


@check_login
@check_id
@check_idAuth
@check_parameters(["status"])
def changeModelStatus(request, result):
    if request.GET["status"] == "true":
        status = True
    else:
        status = False
    models.update_one({"id": int(request.GET["id"])}, {'$set': {"status": status}})
    if status:
        msg = "Normal"
    else:
        msg = "Disabled"
    return HttpResponse(json.dumps({"status": 200, "msg": "Model Status has been successfully set to " + msg}),
                        content_type="application/json")


@check_login
@check_id
@check_idAuth
def deleteModel(request, result):
    models.delete_one({"id": int(request.GET["id"])})
    return HttpResponse(json.dumps({"status": 200}), content_type="application/json")


@check_login
def uploadModel(request):
    try:
        if request.method == 'POST':
            file_obj = request.FILES.get('file')
            mId = request.POST.get('mId')
        if int(mId) == -1:
            result = list(models.find({"author": request.session["username"]}))
            model_id = len(result) + 1
        else:
            model_id = mId
        file_extension = file_obj.name.split(".")[-1]
        filename = request.session["username"] + "_model_" + str(model_id) + utc_now().strftime(
            "_%Y-%m-%d-%H-%M-%S.") + file_extension
        f = open(os.getcwd() + "/models/" + filename, 'wb')
        for chunk in file_obj.chunks():
            f.write(chunk)
        f.close()
        getStructurePic(filename.replace(".onnx", ""))
        return HttpResponse(
            json.dumps({"status": 200, "filename": filename, "structurePic": filename.replace(".onnx", ".svg")}),
            content_type="application/json")
    except Exception as e:
        return HttpResponse(json.dumps({"status": str(Exception), "msg": str(e)}), content_type="application/json")


@check_login
@check_parameters(["type", "id"])
def downloadModel(request):
    # 根据模型id查找
    if request.GET["type"] == '1':
        result = list(models.find({"id": int(request.GET["id"])}))
        if len(result) == 0:
            return json_wrap({"status": 404, "msg": "We can't find model infos based on given ID!"})
        elif result[0]["author"] != request.session["username"] and request.session["role"] != "manager":
            return json_wrap({"status": 501, "msg": "Sorry, you don't have the permission to download this model!"})
    else:
        # 根据订单ID下载模型
        result = list(orders.find({"id": int(request.GET["id"])}))
        if len(result) == 0:
            return json_wrap({"status": 404, "msg": "We can't find model infos based on given ID!"})
        elif result[0]["buyer"] != request.session["username"] and request.session["role"] != "manager":
            return json_wrap({"status": 501, "msg": "Sorry, you don't have the permission to download this model!"})
    filename = os.getcwd() + "/models/" + result[0]['filename']
    file = open(filename, 'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="' + result[0]['filename'] + '"'
    print(response['Content-Disposition'])
    return response


# 得到ONNX模型的结构图
def getStructurePic(filename):
    getDot(filename + ".onnx", filename + ".dot")
    command = 'dot -Tsvg pics/dots/%s.dot -o pics/%s.svg' % (filename, filename)
    os.popen(command)
