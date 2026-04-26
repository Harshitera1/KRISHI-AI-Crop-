def recommend_fertilizer(crop):
    crop = crop.lower()

    if crop == "wheat":
        return "Urea + DAP"

    elif crop == "rice":
        return "NPK + Potash"

    elif crop == "maize":
        return "Nitrogen-rich fertilizer"

    elif crop == "millet":
        return "Organic compost"

    else:
        return "General-purpose fertilizer"