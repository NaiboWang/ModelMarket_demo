"""
Model Management
"""

from django.http import HttpResponse
import json
import os, time
from bson import json_util
from django.http import FileResponse
from .dbconfig import *
from functools import wraps
from .view import check_login


# 检查Id对应模型是否存在
def check_id(f):
    @wraps(f)
    def inner(request, *arg, **kwargs):
        if 'id' in request.GET:
            tid = request.GET['id']
            try:
                res = list(models.find({"id": int(tid)}))
                if len(res) > 0:
                    return f(request, res[0], *arg, **kwargs)
                else:
                    return HttpResponse(
                        json.dumps({"status": 404, "reason": "We can't find model infos based on given ID!"}),
                        content_type="application/json")
            except:
                return HttpResponse(
                    json.dumps({"status": 404, "reason": "We can't find model infos based on given ID!"}),
                    content_type="application/json")
        else:
            return HttpResponse(json.dumps({"status": 404, "reason": "Please specify the model ID!"}),
                                content_type="application/json")
    return inner


# 检查Id对应模型的用户是否有权限操作模型
def check_idAuth(f):
    @wraps(f)
    def inner(request, result, *arg, **kwargs):
        if result['username'] == request.session["username"] or request.session["role"] == "manager":
            return f(request, result, *arg, **kwargs)
        else:
            return HttpResponse(
                json.dumps({"status": 501, "reason": "Sorry, you don't have the permission to do this!"}),
                content_type="application/json")
    return inner


@check_id
def queryModel(request, result):
    return HttpResponse(json.dumps({"status":200, "data": result}, default=json_util.default), content_type="application/json")


def queryModels(request):
    if request.session["role"] == "provider":
        result = models.find({"username": request.session["username"]})
    else:
        result = models.find()
    return HttpResponse(json.dumps({"status":200, "data": list(result)}, default=json_util.default), content_type="application/json")


@check_login
def manageModel(request):
    data = request.POST['paras']
    data = json.loads(data)
    data["username"] = request.session["username"]
    if int(data["id"]) == -1:
        result = list(models.find({}).sort("id", -1).skip(0).limit(1))
        if len(result) == 0:
            data["id"] = 0
        else:
            data["id"] = int(result[0]["id"]) + 1  # 修改id
        models.insert_one(data)
    else:
        result = list(models.find({"id": int(data["id"])}))[0]
        if result['username'] == request.session["username"]:
            models.delete_one({"id": int(data["id"])})
            models.insert_one(data)
            return HttpResponse(json.dumps({"status": 200}), content_type="application/json")
        else:
            return HttpResponse(json.dumps({"status": 400, "reason": "Not correct user, permission denied."}),
                                content_type="application/json")
    return HttpResponse(
        json.dumps({"status": 200, "id": int(data["id"])}), content_type="application/json")


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
            result = list(models.find({"username": request.session["username"]}))
            model_id = len(result) + 1
        else:
            model_id = mId
        file_extension = file_obj.name.split(".")[-1]
        filename = request.session["username"] + "_model_" + str(model_id) + time.strftime("_%Y-%m-%d-%H-%M-%S.",
                                                                                           time.localtime()) + file_extension
        f = open(os.getcwd() + "/models/" + filename, 'wb')
        for chunk in file_obj.chunks():
            f.write(chunk)
        f.close()
        return HttpResponse(json.dumps({"status": 200, "filename": filename}), content_type="application/json")
    except Exception as e:
        return HttpResponse(json.dumps({"status": str(Exception), "reason": str(e)}), content_type="application/json")


@check_id
def downloadModel(request, result):
    filename = os.getcwd() + "/models/" + result['filename']
    file = open(filename, 'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="' + result['filename'] + '"'
    print(response['Content-Disposition'])
    return response
