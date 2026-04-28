import joblib
import pandas as pd
import os

# ✅ Load model once (best practice)
model_path = os.path.join(os.path.dirname(__file__), "../models/crop_model.pkl")
model = joblib.load(model_path)

def predict_crop(data):
    # ✅ Create input dataframe
    input_df = pd.DataFrame([{
        "N": data["N"],
        "P": data["P"],
        "K": data["K"],
        "temperature": data["temperature"],
        "humidity": data["humidity"],
        "ph": data["ph"],
        "rainfall": data["rainfall"]
    }])

    # 🔍 Debug (good for now)
    print("📥 Model Input:")
    print(input_df)

    # ✅ Get probabilities
    probabilities = model.predict_proba(input_df)[0]
    classes = model.classes_

    # ✅ Combine + sort
    results = list(zip(classes, probabilities))
    results = sorted(results, key=lambda x: x[1], reverse=True)

    # 🔍 Debug top predictions
    print("📊 Top Predictions:", results[:3])

    # ✅ Return top 3 crops
    top3 = [
        {"crop": crop, "confidence": round(prob * 100, 2)}
        for crop, prob in results[:3]
    ]

    return top3