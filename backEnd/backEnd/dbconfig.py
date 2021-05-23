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

# 展示了如何多表查询并提取指定字段
models_with_info = models.aggregate(
    [{'$lookup': {'from': "auths", "localField": "author", "foreignField": "username", "as": "author_info"}},
     {'$unwind': {'path': '$author_info', 'preserveNullAndEmptyArrays': True}},
     {'$addFields': {'nickname': "$author_info.nickname"}},
     {'$project': {'author_info': 0}}
     ])


# 根据不同条件查询
def queryTable(table, request, additionalColumns={"_id": 0}, additionalConditions=False, aggregationCondition=False):
    models_with_info = models.aggregate(
        [{'$lookup': {'from': "auths", "localField": "author", "foreignField": "username", "as": "author_info"}},
         {'$unwind': {'path': '$author_info', 'preserveNullAndEmptyArrays': True}},
         {'$addFields': {'nickname': "$author_info.nickname"}},
         {'$project': {'author_info': 0}}
         ])
    pageNum = int(request.POST["pageNum"])
    pageSize = int(request.POST["pageSize"])
    query = request.POST["query"]
    pattern = re.compile(r'.*' + query + '.*', re.I)
    regex = Regex.from_native(pattern)
    regex.flags ^= re.UNICODE
    queryConditions = request.POST["fields"].split(",")
    # 如果有额外的查询条件，使用and语句加入条件
    if additionalConditions:
        # 如果查询字段超过1个，使用or语句合并查询
        if len(queryConditions) >= 2:
            conditions = []
            additionalConditions.append({"$or": conditions})
            for field in queryConditions:
                conditions.append({field: regex})
            query = table.find({"$and": additionalConditions}, additionalColumns)
        else:
            additionalConditions.append({queryConditions[0]: regex})
            query = table.find({"$and": additionalConditions}, additionalColumns)
    # 没有额外的查询条件，直接查询
    else:
        if len(queryConditions) >= 2:
            conditions = []
            for field in queryConditions:
                conditions.append({field: regex})
            query = table.find({"$or": conditions}, additionalColumns)
        else:
            query = table.find({queryConditions[0]: regex}, additionalColumns)
    sortCondition = [(request.POST["sortProp"], int(request.POST["order"]))]
    # .collation({"locale": "en"})不区分大小写
    query.skip(pageSize * (pageNum - 1)).limit(pageSize).collation({"locale": "en"}).sort(sortCondition)
    # 如果有多表联合查询的条件，先写在这
    # if aggregationCondition:
    #     query = query.aggreate(aggregationCondition)
    result = list(query)
    total = query.count()
    return result, total
