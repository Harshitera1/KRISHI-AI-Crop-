from services.crop_service import predict_crop
from services.weather_service import get_weather
from services.soil_service import fetch_soil_data
from services.fertilizer_service import recommend_fertilizer
from services.location_service import find_nearest_location, match_voice_location
from models.soil_model import get_soil_data
import logging
from flask import g
from utils.validation import validate_crop_input
from database.mongo import history_collection

logger = logging.getLogger(__name__)

def get_crop(data):
    # VALIDATION
    errors = validate_crop_input(data)
    if errors:
        return {
            "success": False,
            "errors": errors
        }

    city = data.get("location", "Unknown")
    soil_type = data.get("soil", "Loamy")
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    
    logger.info(
        "Crop recommendation request received",
        extra={
            "event": "crop_request",
            "city": city,
            "latitude": latitude,
            "longitude": longitude,
            "soil_type": soil_type
        }
    )

    # FIRST: Find the nearest location based on coordinates (to get mapped location)
    location_match = find_nearest_location(latitude, longitude)
    region = location_match.get("region", "North")
    nearest_city = location_match.get("location", "Unknown")
    
    logger.info(
        "Location determined for filtering",
        extra={
            "event": "location_determined",
            "nearest_city": nearest_city,
            "region": region,
            "latitude": latitude,
            "longitude": longitude,
            "user_provided_location": city,
            "distance_from_location": location_match.get("distance")
        }
    )

    # GET WEATHER using the MAPPED location (nearest in database), not user input
    weather = get_weather(nearest_city)

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

    # SOIL MAP
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

    # ML INPUT
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

    # PREDICT CROPS FROM ML MODEL
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

    # STRICT REGIONAL CROP FILTERING - CORE FIX
    # Use location service for accurate location matching
    from models.npk_region_model import NPK_RECOMMENDATIONS
    
    # Get approved crops for this region only
    available_crops_in_region = list(NPK_RECOMMENDATIONS.get(region, {}).keys())
    
    logger.info(
        "Regional filtering applied",
        extra={
            "event": "regional_filter",
            "region": region,
            "available_crops": available_crops_in_region,
            "requested_location": city
        }
    )
    
    # STRICT FILTERING: Keep ONLY crops allowed in this region
    filtered_result = []
    for item in result:
        crop_name = item["crop"].lower()
        if crop_name in available_crops_in_region:
            filtered_result.append(item)
    
    # If no crops from ML passed filter, use region's approved crops
    if not filtered_result:
        logger.warning(
            "No ML crops matched region database - using region-approved crops",
            extra={
                "event": "using_region_crops_only",
                "region": region,
                "available_crops": available_crops_in_region,
                "ml_predictions": [x["crop"] for x in result[:3]]
            }
        )
        # Use region's approved crops (NOT ML predictions)
        for crop in list(available_crops_in_region)[:3]:
            filtered_result.append({"crop": crop, "confidence": 0.5})
    else:
        # Sort by confidence and keep top 3
        filtered_result = sorted(filtered_result, key=lambda x: x["confidence"], reverse=True)[:3]
    
    result = filtered_result

    # RERANK based on suitable crops if available
    if suitable_crops:
        reranked_result = []
        
        for item in result:
            crop_name = item["crop"]
            confidence = item["confidence"]
            
            if crop_name in suitable_crops:
                confidence = min(confidence * 1.3, 1.0)
                reranked_result.append({
                    "crop": crop_name,
                    "confidence": round(confidence, 3),
                    "suitable_for_region": True
                })
            else:
                confidence = confidence * 0.7
                reranked_result.append({
                    "crop": crop_name,
                    "confidence": round(confidence, 3),
                    "suitable_for_region": False
                })
        
        reranked_result.sort(key=lambda x: x["confidence"], reverse=True)
        result = [{"crop": item["crop"], "confidence": item["confidence"]} for item in reranked_result]
        
        logger.info(
            "Recommendations reranked based on soil suitability",
            extra={
                "event": "recommendations_reranked",
                "request_id": g.get("request_id"),
                "top_crop": result[0]["crop"],
                "suitable_crops": suitable_crops
            }
        )

    # SAVE HISTORY
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
                "suitable_crops_used": suitable_crops,
                "region": region
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

    # FINAL RESPONSE CHECK
    if not result or not isinstance(result, list) or len(result) == 0:
        logger.error(
            "No results from ML prediction",
            extra={
                "event": "no_results",
                "request_id": g.get("request_id"),
                "city": city,
                "region": region,
                "soil_type": soil_type
            }
        )
        return {
            "success": False,
            "message": "Could not generate recommendations for this region."
        }
    
    recommended_crop = result[0]["crop"]
    
    # GET FERTILIZER RECOMMENDATION
    try:
        fertilizer_rec = recommend_fertilizer(
            recommended_crop,
            latitude=latitude,
            longitude=longitude,
            city=city
        )
        logger.info(
            "Fertilizer recommendation generated",
            extra={
                "event": "fertilizer_generated",
                "crop": recommended_crop,
                "region": fertilizer_rec.get("region")
            }
        )
    except Exception as e:
        logger.error(
            "Fertilizer recommendation error",
            extra={
                "event": "fertilizer_error",
                "request_id": g.get("request_id"),
                "error": str(e)
            }
        )
        fertilizer_rec = {
            "crop": recommended_crop,
            "fertilizer_type": "General NPK",
            "description": "General purpose fertilizer",
            "npk_values": {"N": 100, "P": 50, "K": 40},
            "region": region,
            "dosage": "100 kg/ha Nitrogen, 50 kg/ha Phosphorus, 40 kg/ha Potassium"
        }
    
    logger.info(
        "Crop recommendation completed successfully",
        extra={
            "event": "crop_recommendation_complete",
            "recommended_crop": recommended_crop,
            "region": region,
            "top_3": [item["crop"] for item in result]
        }
    )
    
    return {
        "success": True,
        "recommended_crop": recommended_crop,
        "top_3": result,
        "weather": weather,
        "soil_info": {
            "city": city,
            "soil_type": soil_type,
            "region": region,
            "suitable_crops": suitable_crops
        },
        "fertilizer": fertilizer_rec,
        "mapped_location": nearest_city,
        "user_selected_location": city,
        "region": region
    }
