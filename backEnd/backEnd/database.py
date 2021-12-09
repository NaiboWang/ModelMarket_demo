import pymongo

myclient = pymongo.MongoClient('mongodb://localhost:27017/')
mydb = myclient['modelmarket']
mycol = mydb["auths"]
models = mydb["models"]  # 生成新任务并返回ID