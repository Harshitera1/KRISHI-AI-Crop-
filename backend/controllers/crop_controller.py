from services.crop_service import recommend_crop
from services.weather_service import get_weather

def get_crop(data):
    city = data.get("location")
    soil = data.get("soil")

    if not city or not soil:
        return {"success": False, "msg": "Missing soil or location"}

    weather = get_weather(city)

    if not weather["success"]:
        return weather

    crop = recommend_crop(
        soil,
        weather["temperature"],
        weather["humidity"]
    )

    return {
        "success": True,
        "recommended_crop": crop,
        "weather": weather
    }