from .view import check_parameters
from .tools import json_wrap
from .dbconfig import *
from bson.objectid import ObjectId

@check_parameters(["id"])
def queryLog(request):
    try:
        result = logs.find_one({'_id':ObjectId(request.GET["id"])},{"_id":0,"help":0})
    except:
        return HttpResponse(
            json.dumps({"status": 404, "msg": "We can't find log info based on given ID!"}),
            content_type="application/json")
    if result == None:
        return HttpResponse(
            json.dumps({"status": 404, "msg": "We can't find log info based on given ID!"}),
            content_type="application/json")
    if request.session["role"] == "manager":
        return json_wrap({"status": 200, "data": result}, no_log=True)
    else:
        return json_wrap({"status": 503, "msg": "Sorry, you don't have the permission to see this information!"})


@check_parameters(["query", "pageNum", "pageSize", "fields", "sortProp", "order"])
def queryLogs(request):
    if request.session["role"] == "manager":
        result, total = queryTable(logs, request,additionalColumns={'help':0})
        return json_wrap({"status": 200, "data": result, "total": total}, no_log=True)
    else:
        return json_wrap({"status": 503, "msg": "Sorry, you don't have the permission to see this information!"})