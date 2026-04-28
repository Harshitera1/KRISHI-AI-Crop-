import streamlit as st
import requests

# Page config
st.set_page_config(page_title="KRISHI AI", layout="centered")

# ---------- CUSTOM STYLING ----------
st.markdown("""
<style>
.main {
    background-color: #0e1117;
}
h1, h2, h3 {
    text-align: center;
}
.stButton>button {
    width: 100%;
    border-radius: 10px;
    height: 3em;
    background-color: #22c55e;
    color: white;
    font-size: 16px;
}
.block-container {
    padding-top: 2rem;
}
</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.title("🌾 KRISHI AI")
st.subheader("Smart Crop & Fertilizer Recommendation System")

st.markdown("---")

# ---------- INPUT SECTION ----------
st.markdown("### 📥 Enter Farm Details")

col1, col2 = st.columns(2)

with col1:
    soil = st.selectbox("🌱 Soil Type", ["Loamy", "Sandy", "Clay"])
    N = st.number_input("Nitrogen (N)", 0, 140, 90)
    P = st.number_input("Phosphorus (P)", 0, 140, 40)

with col2:
    city = st.text_input("📍 Location", "Delhi")
    K = st.number_input("Potassium (K)", 0, 140, 40)
    ph = st.number_input("Soil pH", 0.0, 14.0, 6.5)

st.markdown("---")

# ---------- BUTTON ----------
if st.button("🚀 Get Recommendation"):

    with st.spinner("Analyzing soil + weather + ML model..."):
        try:
            res = requests.post(
                "http://127.0.0.1:5001/api/crop/recommend",
                json={
                    "location": city,
                    "soil": soil,
                    "N": N,
                    "P": P,
                    "K": K,
                    "ph": ph
                }
            )

            data = res.json()

            if data["success"]:

                st.success(f"🌱 Best Crop: {data['recommended_crop']}")

                # 🏆 Top 3
                st.markdown("### 🏆 Top 3 Crop Recommendations")
                for i, item in enumerate(data["top_3"], start=1):
                    st.write(f"{i}. {item['crop']} ({item['confidence']}%)")

                # 🌦 Weather
                st.markdown("### 🌦 Weather Insights")

                col1, col2, col3 = st.columns(3)

                col1.metric("🌡 Temperature", f"{data['weather']['temperature']} °C")
                col2.metric("💧 Humidity", f"{data['weather']['humidity']}%")
                col3.metric("☁️ Condition", data['weather']['condition'])

            else:
                st.error(data["msg"])

        except Exception:
            st.error("⚠️ Backend not running or connection error")