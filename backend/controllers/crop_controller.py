from services.crop_service import predict_crop
from services.weather_service import get_weather
from services.soil_service import fetch_soil_data
from models.soil_model import get_soil_data
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
    soil_type = data.get("soil", "Loamy")

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

    # 🌱 SOIL MAP & SUITABLE CROPS
    soil_map = {
        "Loamy": 6.5,
        "Sandy": 5.5,
        "Clay": 7.5,
        "Silt": 6.0
    }

    # Try to fetch soil data for location-based crops
    soil_db_data = get_soil_data(city, soil_type)
    suitable_crops = []
    
    if soil_db_data:
        suitable_crops = soil_db_data.get("crops", [])
        logger.info(
            "Soil data found for region-based recommendations",
            extra={
                "event": "soil_data_loaded",
                "city": city,
                "soil_type": soil_type,
                "suitable_crops": suitable_crops
            }
        )

    # 📊 ML INPUT
    ml_input = {
        "N": data.get("N", 90),
        "P": data.get("P", 40),
        "K": data.get("K", 40),
        "temperature": weather.get("temperature", 25),
        "humidity": weather.get("humidity", 50),
        "ph": data.get("ph", soil_map.get(soil_type, 6.5)),
        "rainfall": weather.get("humidity", 50) * 3
    }

    logger.info(
        "ML input prepared",
        extra={
            "event": "ml_input",
            "request_id": g.get("request_id"),
            "data": ml_input,
            "location": city,
            "soil_type": soil_type
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

    # 🔥 FILTER & RERANK RECOMMENDATIONS based on suitable crops
    if suitable_crops:
        # Boost confidence for crops that are suitable for this region
        reranked_result = []
        
        for item in result:
            crop_name = item["crop"]
            confidence = item["confidence"]
            
            # If crop is suitable for this region, boost its confidence
            if crop_name in suitable_crops:
                confidence = min(confidence * 1.3, 1.0)  # Boost by 30%
                reranked_result.append({
                    "crop": crop_name,
                    "confidence": round(confidence, 3),
                    "suitable_for_region": True
                })
            else:
                # Lower confidence for unsuitable crops
                confidence = confidence * 0.7  # Reduce by 30%
                reranked_result.append({
                    "crop": crop_name,
                    "confidence": round(confidence, 3),
                    "suitable_for_region": False
                })
        
        # Re-sort by confidence
        reranked_result.sort(key=lambda x: x["confidence"], reverse=True)
        
        # Remove the internal flag before returning
        result = [{"crop": item["crop"], "confidence": item["confidence"]} for item in reranked_result]
        
        logger.info(
            "Recommendations reranked based on soil suitability",
            extra={
                "event": "recommendations_reranked",
                "request_id": g.get("request_id"),
                "original_top": result[0]["crop"],
                "suitable_crops": suitable_crops
            }
        )

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
                },
                "soil_type": soil_type,
                "suitable_crops_used": suitable_crops
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
        "weather": weather,
        "soil_info": {
            "city": city,
            "soil_type": soil_type,
            "suitable_crops": suitable_crops
        }
    }