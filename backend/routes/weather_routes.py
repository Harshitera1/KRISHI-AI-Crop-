from flask import Blueprint, jsonify
from controllers.weather_controller import fetch_weather

weather_bp = Blueprint("weather", __name__)

@weather_bp.route("/<city>", methods=["GET"])
def get_weather_route(city):
    result = fetch_weather(city)
    return jsonify(result)