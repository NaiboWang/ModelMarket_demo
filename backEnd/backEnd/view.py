from django.http import HttpResponse
import pymongo
import json
import os, time
from bson import json_util
from functools import wraps

myclient = pymongo.MongoClient('mongodb://localhost:27017/')
mydb = myclient['modelmarket']
mycol = mydb["auths"]
models = mydb["models"]  # 生成新任务并返回ID


def check_login(f):
    @wraps(f)
    def inner(request, *arg, **kwargs):
        if request.session.get('is_login') == '1':
            return f(request, *arg, **kwargs)
        else:
            return HttpResponse(json.dumps({"status": 301, "error": "Not logged in!"}), content_type="application/json")

    return inner


def hello(request):
    return HttpResponse("Hello world ! ")


def queryModels(request):
    if "username" in request.GET:
        result = models.find({"username": request.GET["username"]})
    else:
        result = models.find()
    return HttpResponse(json.dumps(list(result)), content_type="application/json")


def login(request):
    result = mycol.find({"username": request.POST['username']})
    r = list(result)
    if len(r) == 0:  # 没找到值
        result = {"status": 404, "error": "User not found!"}
        print("User not found")
    else:
        item = r[0]
        if item["pswd"] != request.POST['pass']:
            result = {"status": 201, "error": "Wrong password!"}
        else:
            result = {"status": 200, "role": item["role"]}
            request.session['is_login'] = '1'
            request.session["username"] = request.POST["username"]
            request.session["role"] = item["role"]
    return HttpResponse(json.dumps(result), content_type="application/json")


@check_login
def getIdentity(request):
    return HttpResponse(
        json.dumps({"status": 200, "role": request.session["role"], "username": request.session["username"]}),
        content_type="application/json")


def manageModel(request):
    data = request.POST['paras']
    data = json.loads(data)
    if int(data["id"]) == -1:
        count = mycol.find({}).count()
        data["id"] = count  # 修改id
        mycol.insert_one(data)
    else:
        mycol.delete_one({"id": int(data["id"])})
        mycol.insert_one(data)
    return HttpResponse(data["id"])


def deleteService(request):
    if 'id' in request.GET:
        tid = request.GET['id']
        myquery = {"id": int(tid)}
        newvalues = {"$set": {"id": -2}}  # 删除就是将服务id变成-2，并没有真正删除
        mycol.update_one(myquery, newvalues)
    return HttpResponse("Done!")


@check_login
def uploadModel(request):
    try:
        if request.method == 'POST':
            file_obj = request.FILES.get('file')
        print("username",request.session["username"])
        result = list(models.find({"username": request.session["username"]}))
        model_id = len(result) + 1
        file_extension = file_obj.name.split(".")[-1]
        filename = request.session["username"] + "_model_" + str(model_id) + time.strftime("_%Y-%m-%d-%H-%M-%S.", time.localtime()) + file_extension
        f = open(os.getcwd() + "/models/" + filename, 'wb')
        for chunk in file_obj.chunks():
            f.write(chunk)
        f.close()
        return HttpResponse(json.dumps({"status":200, "filename":filename}), content_type="application/json")
    except Exception as e:
        return HttpResponse(json.dumps({"status": str(Exception), "reason": str(e)}), content_type="application/json")

