from models.farm_model import create_farm

def add_farm(data):
    if not data.get("username"):
        return {"success": False, "msg": "Username required"}

    create_farm(data)
    return {"success": True, "msg": "Farm added successfully"}