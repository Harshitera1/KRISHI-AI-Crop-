import joblib
import pandas as pd
import os

# Absolute safe path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "../models/crop_model.pkl")

# Load model once
try:
    model = joblib.load(MODEL_PATH)
    print("✅ Model loaded successfully")
except Exception as e:
    print("❌ Model loading failed:", e)
    model = None


def predict_crop(data):
    if model is None:
        return "Model not loaded"

    try:
        input_df = pd.DataFrame([{
            "N": data.get("N", 0),
            "P": data.get("P", 0),
            "K": data.get("K", 0),
            "temperature": data.get("temperature", 0),
            "humidity": data.get("humidity", 0),
            "ph": data.get("ph", 7),
            "rainfall": data.get("rainfall", 0)
        }])

        # 🔥 Get probabilities
        probs = model.predict_proba(input_df)[0]
        crops = model.classes_

        # 🔥 Top 3 crops
        top_indices = probs.argsort()[-3:][::-1]

        top_3 = []
        for i in top_indices:
            top_3.append({
                "crop": crops[i],
                "confidence": round(float(probs[i]), 3)
            })

        return top_3

    except Exception as e:
        print("❌ Prediction error:", e)
        return "Prediction error"