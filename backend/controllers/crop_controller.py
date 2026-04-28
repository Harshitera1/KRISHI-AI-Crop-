from services.crop_service import predict_crop
from services.weather_service import get_weather

def get_crop(data):
    city = data.get("location")

    # 🌦 Get weather
    weather = get_weather(city)

    if not weather["success"]:
        return weather

    # ✅ Soil mapping
    soil_map = {
        "Loamy": 6.5,
        "Sandy": 5.5,
        "Clay": 7.5
    }

    # ✅ ML input (properly indented INSIDE function)
    ml_input = {
        "N": data.get("N", 90),
        "P": data.get("P", 40),
        "K": data.get("K", 40),

        "temperature": weather.get("temperature", 25),
        "humidity": weather.get("humidity", 50),

        "ph": data.get("ph", soil_map.get(data.get("soil"), 6.5)),

        # ✅ Dynamic rainfall (important fix)
        "rainfall": weather.get("humidity", 50) * 3
    }

    print("🚀 Final ML Input:", ml_input)

    top_crops = predict_crop(ml_input)

    return {
        "success": True,
        "recommended_crop": top_crops[0]["crop"],
        "top_3": top_crops,
        "weather": weather
    }