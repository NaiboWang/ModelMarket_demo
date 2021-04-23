import re
import pymongo
from bson import Regex

myclient = pymongo.MongoClient('mongodb://localhost:27017/')
mydb = myclient['modelmarket']
myauths = mydb["auths"]
models = mydb["models"]
orders = mydb["orders"]


def queryTable(table, request):
    pageNum = int(request.POST["pageNum"])
    pageSize = int(request.POST["pageSize"])
    query = request.POST["query"]
    pattern = re.compile(r'.*' + query + '.*', re.I)
    regex = Regex.from_native(pattern)
    regex.flags ^= re.UNICODE
    result = list(table.find({"modelName": regex}).skip(pageSize*(pageNum-1)).limit(pageSize))
    total = list(table.find({"modelName": regex}))
    return result, len(total)
