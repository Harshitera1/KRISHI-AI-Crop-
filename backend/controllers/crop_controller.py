from services.crop_service import predict_crop
from services.weather_service import get_weather
import logging
from flask import g
from utils.validation import validate_crop_input
from database.mongo import history_collection

logger = logging.getLogger(__name__)

def get_crop(data):

    # 🔥 VALIDATION
    errors = validate_crop_input(data)
    if errors:
        return {
            "success": False,
            "errors": errors
        }

    city = data.get("location")

    # 🌦 WEATHER
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

    # 🌱 SOIL
    soil_map = {
        "Loamy": 6.5,
        "Sandy": 5.5,
        "Clay": 7.5
    }

    # 📊 ML INPUT
    ml_input = {
        "N": data.get("N", 90),
        "P": data.get("P", 40),
        "K": data.get("K", 40),
        "temperature": weather.get("temperature", 25),
        "humidity": weather.get("humidity", 50),
        "ph": data.get("ph", soil_map.get(data.get("soil"), 6.5)),
        "rainfall": weather.get("humidity", 50) * 3
    }

    logger.info(
        "ML input prepared",
        extra={
            "event": "ml_input",
            "request_id": g.get("request_id"),
            "data": ml_input
        }
    )

    # 🤖 PREDICT
    result = predict_crop(ml_input)

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

    # 💾 SAVE HISTORY (FIXED)
    try:
        if history_collection is not None:
            history_collection.insert_one({
                "user": g.get("user"),
                "input": data,
                "result": [
                    {
                        "crop": str(item["crop"]),
                        "confidence": float(item["confidence"])
                    }
                    for item in result
                ],
                "weather": {
                    "temperature": float(weather.get("temperature", 0)),
                    "humidity": float(weather.get("humidity", 0)),
                    "city": weather.get("city"),
                    "condition": weather.get("condition")
                }
            })
    except Exception as e:
        logger.error(
            "History save failed",
            extra={
                "event": "history_error",
                "request_id": g.get("request_id"),
                "error": str(e)
            }
        )

    # ✅ FINAL RESPONSE
    return {
        "success": True,
        "recommended_crop": result[0]["crop"],
        "top_3": result,
        "weather": weather
    }