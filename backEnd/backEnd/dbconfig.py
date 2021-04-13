import pymongo

myclient = pymongo.MongoClient('mongodb://localhost:27017/')
mydb = myclient['modelmarket']
myauths = mydb["auths"]
models = mydb["models"]