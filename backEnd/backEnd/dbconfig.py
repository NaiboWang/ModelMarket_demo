import json
import re
import pymongo
from bson import Regex

myclient = pymongo.MongoClient('mongodb://localhost:27017/')
mydb = myclient['modelmarket']
myauths = mydb["auths"]
models = mydb["models"]
orders = mydb["orders"]
logs = mydb["logs"]


# {
#   $project: {
#     _id: 1,
#     product: 1,
#     money: 1,
#     name: 1
#   }
# }
# https://blog.csdn.net/u011113654/article/details/80353013

# # 展示了如何多表查询并提取指定字段
# models_with_info = models.aggregate(
#     [{'$lookup': {'from': "auths", "localField": "author", "foreignField": "username", "as": "author_info"}},
#      {'$unwind': {'path': '$author_info', 'preserveNullAndEmptyArrays': True}},
#      {'$addFields': {'nickname': "$author_info.nickname"}},
#      {'$project': {'author_info': 0}}
#      ])

# 生成简单查询条件
def getQueryCondition(queryConditions):
    conditions = []
    for fieldInfo in queryConditions:
        if fieldInfo["type"] == 'text' or fieldInfo["type"] == 'array' or fieldInfo["type"] == 'datetime':
            pattern = re.compile(r'.*' + fieldInfo['query'] + '.*', re.I)
            regex = Regex.from_native(pattern)
            regex.flags ^= re.UNICODE
            conditions.append({fieldInfo["name"]: regex})
        elif fieldInfo["type"] == 'number':
            if fieldInfo["query"] != "":
                try:
                    num = float(fieldInfo["query"])
                    conditions.append({fieldInfo["name"]: {"$eq": num}})
                except:
                    conditions.append({fieldInfo["name"]: {"$eq": -99999}})
    return {"$or": conditions}


# 根据不同条件查询
def queryTable(table, request, additionalColumns={"_id": 0}, additionalConditions=[], aggregationConditions=False):
    pageNum = int(request.POST["pageNum"])
    pageSize = int(request.POST["pageSize"])
    queryConditions = json.loads(request.POST["fields"])
    conditions = getQueryCondition(queryConditions)
    if 'advance' in request.POST and request.POST['advance'] == '1':
        queryFields = json.loads(request.POST["queryFields"])
        multiConditions = json.loads(request.POST["multiConditions"])
        for field in queryFields:
            query_t = multiConditions[field['value']]
            if query_t == '':
                continue
            if 'type' in field:
                if field['type'] == 'datetime':
                    pass
            else:
                pattern_t = re.compile(r'.*' + query_t + '.*', re.I)
                regex_t = Regex.from_native(pattern_t)
                regex_t.flags ^= re.UNICODE
                additionalConditions.append({field['value']: regex_t})
    # CTRL + ALT + SHIFT + J同时选中相同单词
    if aggregationConditions:
        aggregationConditionsT = aggregationConditions.copy()
        if additionalConditions:
            additionalConditions.append(conditions)
            conditions = {"$and": additionalConditions}
        aggregationConditionsT.append({'$match': conditions})
        total = len(table.aggregate(aggregationConditionsT)._CommandCursor__data)
        # 注意顺序，应该先sort再skip和limit！！！
        aggregationConditionsT.append({"$sort": {request.POST["sortProp"]: int(request.POST["order"])}})
        aggregationConditionsT.append({'$skip': pageSize * (pageNum - 1)})
        aggregationConditionsT.append({"$limit": pageSize})
        result = list(table.aggregate(aggregationConditionsT))
    else:
        # 如果有额外的查询条件，使用and语句加入条件
        if additionalConditions:
            additionalConditions.append(conditions)
            query = table.find({"$and": additionalConditions}, additionalColumns)
        # 没有额外的查询条件，直接查询
        else:
            query = table.find(conditions, additionalColumns)
        sortCondition = [(request.POST["sortProp"], int(request.POST["order"]))]
        # .collation({"locale": "en"})不区分大小写
        query.sort(sortCondition).skip(pageSize * (pageNum - 1)).limit(pageSize).collation({"locale": "en"})
        result = list(query)
        total = query.count()
    return result, total
