from database.mongo import db

farm_collection = db["farms"]

def create_farm(data):
    return farm_collection.insert_one(data)

def get_farms_by_user(username):
    return farm_collection.find({"username": username})