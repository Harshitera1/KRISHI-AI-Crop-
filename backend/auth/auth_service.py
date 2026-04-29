from flask_bcrypt import Bcrypt
from database.mongo import users_collection

bcrypt = Bcrypt()

def signup_user(username, password):
    existing_user = users_collection.find_one({"username": username})

    if existing_user:
        return {"success": False, "message": "User already exists"}

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

    users_collection.insert_one({
        "username": username,
        "password": hashed_password
    })

    return {"success": True, "message": "User created successfully"}


def login_user(username, password):
    user = users_collection.find_one({"username": username})

    if not user:
        return {"success": False, "message": "User not found"}

    if not bcrypt.check_password_hash(user["password"], password):
        return {"success": False, "message": "Invalid password"}

    return {"success": True}