import streamlit as st
import requests

# Page config
st.set_page_config(page_title="KRISHI AI", layout="centered")

st.title("🌾 KRISHI AI Crop Recommendation System")

st.markdown("### Enter your farm details")

# Inputs
soil = st.selectbox("🌱 Select Soil Type", ["Loamy", "Sandy", "Clay"])
city = st.text_input("📍 Enter Location", "Delhi")



if st.button("Get Recommendation"):

    with st.spinner("Fetching data..."):
        try:
            res = requests.post(
                "http://127.0.0.1:5001/api/crop/recommend",
                json={
                    "soil": soil,
                    "location": city
                }
            )

            data = res.json()

            if data["success"]:
                st.success(f"🌱 Recommended Crop: {data['recommended_crop']}")

                st.markdown("## 🌦 Weather Details")
                st.write(f"🌡 Temperature: {data['weather']['temperature']} °C")
                st.write(f"💧 Humidity: {data['weather']['humidity']}%")
                st.write(f"☁️ Condition: {data['weather']['condition']}")

                # ✅ ADD HERE (IMPORTANT)
                fert_res = requests.get(
                    f"http://127.0.0.1:5001/api/fertilizer/{data['recommended_crop']}"
                )

                fert_data = fert_res.json()

                st.markdown("## 🧪 Fertilizer Recommendation")
                st.success(f"Recommended Fertilizer: {fert_data['fertilizer']}")

            else:
                st.error(data["msg"])

        except Exception as e:
            st.error("⚠️ Backend not running or connection error")