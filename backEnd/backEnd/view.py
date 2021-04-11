from django.http import HttpResponse
import pymongo
import json
import os, time
from bson import json_util
from functools import wraps

def hello(request):
    return HttpResponse("Hello world ! ")

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

@check_login
def getIdentity(request):
    return HttpResponse(
        json.dumps({"status": 200, "role": request.session["role"], "username": request.session["username"]}),
        content_type="application/json")

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
def logout(request):
    request.session.flush()
    return HttpResponse(json.dumps({"status": 200, }), content_type="application/json")

def register(request):
    result = mycol.find({"username": request.POST['username']})
    r = list(result)
    if len(r) == 0:  # 没找到值
        user = {"username": request.POST['username'], "pswd": request.POST['pass'], "role":request.POST['role']}
        mycol.insert_one(user)
        return HttpResponse(json.dumps({"status": 200}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({"status":302, "reason":"User already exists!"}), content_type="application/json")

def queryModel(request):
    result = models.find({"id": int(request.GET["id"])})
    return HttpResponse(json.dumps(list(result)[0], default=json_util.default), content_type="application/json")


def queryModels(request):
    if request.session["role"] != "user":
        result = models.find({"username": request.session["username"]})
    else:
        result = models.find()
    return HttpResponse(json.dumps(list(result), default=json_util.default), content_type="application/json")

@check_login
def manageModel(request):
    data = request.POST['paras']
    data = json.loads(data)
    data["username"] = request.session["username"]
    if int(data["id"]) == -1:
        result = list(models.find({}).sort("id",-1).skip(0).limit(1))
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
            return HttpResponse(json.dumps({"status": 400, "reason":"Not correct user, permission denied."}), content_type="application/json")
    return HttpResponse(
        json.dumps({"status": 200, "id": int(data["id"])}), content_type="application/json")

@check_login
def deleteModel(request):
    if 'id' in request.GET:
        tid = request.GET['id']
        result = list(models.find({"id": int(tid)}))[0]
        if result['username'] == request.session["username"]:
            try:
                filename = os.getcwd() + "/models/" + result['filename']
                os.remove(filename)
            except:
                pass
            models.delete_one({"id": int(tid)})
            return HttpResponse(json.dumps({"status": 200}), content_type="application/json")
        else:
            return HttpResponse(json.dumps({"status": 400, "reason":"Not correct user, permission denied."}), content_type="application/json")


@check_login
def uploadModel(request):
    try:
        if request.method == 'POST':
            file_obj = request.FILES.get('file')
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

