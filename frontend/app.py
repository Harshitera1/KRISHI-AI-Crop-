import streamlit as st
import requests
import speech_recognition as sr
from gtts import gTTS
import os

# ---------- CONFIG ----------
st.set_page_config(page_title="KRISHI AI", layout="wide")

# ---------- STYLING ----------
st.markdown("""
<style>

/* INPUT TEXT FIELDS */
.stTextInput input {
    background-color: rgba(255,255,255,0.15) !important;
    color: white !important;
    border: 1px solid #22c55e !important;
    border-radius: 10px;
}

/* NUMBER INPUT */
.stNumberInput input {
    background-color: rgba(255,255,255,0.15) !important;
    color: white !important;
    border: 1px solid #22c55e !important;
    border-radius: 10px;
}
.stTextInput input:focus, 
.stNumberInput input:focus {
    border: 2px solid #4ade80 !important;
    box-shadow: 0 0 10px #22c55e;
}

/* SELECTBOX */
.stSelectbox div {
    background-color: rgba(255,255,255,0.15) !important;
    color: white !important;
    border-radius: 10px;
}

/* DROPDOWN TEXT */
.stSelectbox span {
    color: white !important;
}


/* FIX LABEL TEXT */
label {
    color: #bbf7d0 !important;
    font-weight: 600;
}
.stApp {
    background: 
        linear-gradient(rgba(0,0,0,0.55), rgba(0,0,0,0.75)),
        url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1920&q=80");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}


</style>

""", unsafe_allow_html=True)

# ---------- SESSION ----------
if "token" not in st.session_state:
    st.session_state.token = None

# ---------- VOICE ----------
def get_voice_input():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Speak city and soil (e.g., Delhi loamy)...")
        audio = r.listen(source)

    try:
        return r.recognize_google(audio)
    except:
        return None

def speak(text):
    tts = gTTS(text)
    tts.save("output.mp3")
    os.system("afplay output.mp3")

# ---------- HEADER ----------
st.title("🌾 KRISHI AI")
st.markdown("### 🌱 Smart Crop Recommendation System")

# ---------- AUTH ----------
if st.session_state.token is None:

    st.markdown("## 🔐 Login / Signup")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Signup"):
            res = requests.post(
                "http://127.0.0.1:5001/api/auth/signup",
                json={"username": username, "password": password}
            )
            st.success(res.json().get("message", "Done"))

    with col2:
        if st.button("Login"):
            res = requests.post(
                "http://127.0.0.1:5001/api/auth/login",
                json={"username": username, "password": password}
            )
            data = res.json()

            if data.get("success"):
                st.session_state.token = data["token"]
                st.success("Login successful")
                st.rerun()
            else:
                st.error(data.get("message"))

# ---------- MAIN ----------
else:

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section">', unsafe_allow_html=True)

        soil = st.selectbox("🌱 Soil Type", ["Loamy", "Sandy", "Clay"])
        city = st.text_input("📍 City", "Delhi")

        if st.button("🎤 Speak Input"):
            voice_text = get_voice_input()
            if voice_text:
                st.success(f"Detected: {voice_text}")
                parts = voice_text.lower().split()

                if "delhi" in parts:
                    city = "Delhi"
                if "loamy" in parts:
                    soil = "Loamy"
                if "sandy" in parts:
                    soil = "Sandy"
                if "clay" in parts:
                    soil = "Clay"

        st.markdown('</div>', unsafe_allow_html=True)

    # ---------- AUTO SOIL ----------
    N = P = K = ph = None

    try:
        soil_res = requests.get(
            f"http://127.0.0.1:5001/api/soil/data?city={city}&soil_type={soil}",
            headers={"Authorization": f"Bearer {st.session_state.token}"}
        )

        if soil_res.json()["success"]:
            soil_data = soil_res.json()["data"]

            N = soil_data["N"]
            P = soil_data["P"]
            K = soil_data["K"]
            ph = soil_data["pH"]

            st.success("🌱 Soil data auto-loaded")

    except:
        pass

    with col2:
        st.markdown('<div class="section">', unsafe_allow_html=True)

        N = st.number_input("Nitrogen (N)", min_value=0, max_value=500, value=int(N) if N else 90)
        P = st.number_input("Phosphorus (P)", min_value=0, max_value=500, value=int(P) if P else 40)
        K = st.number_input("Potassium (K)", min_value=0, max_value=500, value=int(K) if K else 40)

        st.markdown('</div>', unsafe_allow_html=True)

    # ---------- WEATHER ----------
    weather_data = {}
    try:
        w = requests.get(f"http://127.0.0.1:5001/api/weather/{city}")
        weather_data = w.json()["weather"]
    except:
        pass

    # ---------- PREDICT ----------
    if st.button("🚀 Get Recommendation"):

        res = requests.post(
            "http://127.0.0.1:5001/api/crop/recommend",
            headers={"Authorization": f"Bearer {st.session_state.token}"},
            json={
                "location": city,
                "soil": soil,
                "N": N,
                "P": P,
                "K": K,
                "ph": ph,
                "temperature": weather_data.get("temperature", 25),
                "humidity": weather_data.get("humidity", 50),
                "rainfall": 100
            }
        )

        data = res.json()

        if data.get("success"):

            st.markdown(f"""
            <div class="result-box">
            🌾 Best Crop: {data['recommended_crop']}
            </div>
            """, unsafe_allow_html=True)

            speak(f"Best crop is {data['recommended_crop']}")

            # TOP 3
            st.markdown("### 🏆 Top 3 Crops")

            cols = st.columns(3)
            for i, item in enumerate(data["top_3"]):
                cols[i].markdown(f"""
                <div class="card">
                <h3>{item['crop']}</h3>
                <p>{round(item['confidence']*100, 2)}%</p>
                </div>
                """, unsafe_allow_html=True)

            # WEATHER
            st.markdown("### 🌦 Weather")

            col1, col2, col3 = st.columns(3)
            col1.metric("🌡 Temp", f"{weather_data.get('temperature')} °C")
            col2.metric("💧 Humidity", f"{weather_data.get('humidity')}%")
            col3.metric("☁ Condition", weather_data.get("condition"))

        else:
            st.error(data.get("message"))

    # ---------- HISTORY ----------
    if st.button("📜 View History"):
        res = requests.get(
            "http://127.0.0.1:5001/api/history/",
            headers={"Authorization": f"Bearer {st.session_state.token}"}
        )

        data = res.json()

        if data.get("success"):
            st.markdown("### 📜 History")

            for item in data["history"]:
                st.markdown(f"""
                <div class="card">
                📍 {item['input']['location']} <br>
                🌾 {item['result'][0]['crop']}
                </div>
                """, unsafe_allow_html=True)