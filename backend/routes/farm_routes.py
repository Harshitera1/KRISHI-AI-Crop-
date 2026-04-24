from flask import Blueprint, request, jsonify
from controllers.farm_controller import add_farm

farm_bp = Blueprint("farm", __name__)

@farm_bp.route("/add", methods=["POST"])
def add():
    data = request.json
    result = add_farm(data)
    return jsonify(result)