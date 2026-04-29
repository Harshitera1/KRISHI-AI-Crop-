from flask import Blueprint, request, jsonify
from controllers.crop_controller import get_crop
from auth.auth_middleware import token_required


crop_bp = Blueprint("crop", __name__)

@crop_bp.route("/recommend", methods=["POST"])
@token_required   # 🔥 ADD THIS
def recommend():
    data = request.json
    result = get_crop(data)
    return jsonify(result)