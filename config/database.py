from pymongo import MongoClient

uri = "mongodb+srv://GymPal:Gwencana@cluster0.yimmfp3.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(uri)

db = client.Warehouse_microservice_api

datas = db["datas"]

users = db["users"]
