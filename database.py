from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client['logistics']

trucks_collection = db["trucks"]
orders_collection = db["orders"]

def get_trucks_collection():
    return trucks_collection

def get_orders_collection():
    return orders_collection
