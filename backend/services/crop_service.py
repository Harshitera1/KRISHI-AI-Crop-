def recommend_crop(soil, temperature, humidity):
    soil = soil.lower()

    if soil == "loamy":
        if 20 <= temperature <= 30:
            return "Wheat"
        else:
            return "Maize"

    elif soil == "sandy":
        if temperature > 30:
            return "Millet"
        else:
            return "Groundnut"

    elif soil == "clay":
        if humidity > 50:
            return "Rice"
        else:
            return "Barley"

    else:
        return "Maize"