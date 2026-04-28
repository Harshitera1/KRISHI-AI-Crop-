from services.crop_service import predict_crop
from services.weather_service import get_weather
import logging
from flask import g

logger = logging.getLogger(__name__)

def get_crop(data):
    # ✅ Basic validation
    city = data.get("location")
    if not city:
        return {
            "success": False,
            "message": "Location is required"
        }

    # 🌦 Get weather
    weather = get_weather(city)

    if not weather.get("success"):
        logger.error(
            "Weather fetch failed",
            extra={
                "event": "weather_error",
                "request_id": g.get("request_id"),
                "city": city,
                "response": weather
            }
        )
        return weather

    # ✅ Soil mapping
    soil_map = {
        "Loamy": 6.5,
        "Sandy": 5.5,
        "Clay": 7.5
    }

    # ✅ ML input
    ml_input = {
        "N": data.get("N", 90),
        "P": data.get("P", 40),
        "K": data.get("K", 40),
        "temperature": weather.get("temperature", 25),
        "humidity": weather.get("humidity", 50),
        "ph": data.get("ph", soil_map.get(data.get("soil"), 6.5)),
        "rainfall": weather.get("humidity", 50) * 3
    }

    # 🔥 Structured logging
    logger.info(
        "ML input prepared",
        extra={
            "event": "ml_input",
            "request_id": g.get("request_id"),
            "data": ml_input
        }
    )

    # 🔥 Prediction
    result = predict_crop(ml_input)

    # ❌ Handle ML errors
    if not isinstance(result, list):
        logger.error(
            "ML prediction failed",
            extra={
                "event": "ml_error",
                "request_id": g.get("request_id"),
                "message": result
            }
        )
        return {
            "success": False,
            "message": result
        }

    # ✅ Success
    return {
        "success": True,
        "recommended_crop": result[0]["crop"],
        "top_3": result,
        "weather": weather
    }