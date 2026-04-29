import streamlit as st
import requests
import speech_recognition as sr
from gtts import gTTS
import os

# ---------- CONFIG ----------
st.set_page_config(page_title="KRISHI AI - Smart Crop Recommendation", layout="wide")

# ---------- AGRICULTURAL STYLE ----------
st.markdown("""
<style>
* {
    margin: 0;
    padding: 0;
}

body {
    background: linear-gradient(135deg, #1a4d2e 0%, #2d8659 50%, #8b7355 100%);
    background-attachment: fixed;
    font-family: 'Segoe UI', Arial, sans-serif;
}

.main {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 15px;
    padding: 30px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.header-container {
    text-align: center;
    margin-bottom: 30px;
    padding: 20px;
    background: linear-gradient(135deg, #2d8659 0%, #1a4d2e 100%);
    border-radius: 15px;
    color: white;
    border-left: 5px solid #ffc107;
    border-right: 5px solid #ffc107;
}

.header-container h1 {
    font-size: 2.5em;
    margin-bottom: 5px;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.header-container p {
    font-size: 0.95em;
    opacity: 0.9;
    margin-top: 5px;
}

h2, h3 {
    color: #1a4d2e;
    border-bottom: 3px solid #2d8659;
    padding-bottom: 10px;
    margin-bottom: 15px;
}

.soil-section, .location-section, .results-section {
    background: #f8f9fa;
    padding: 20px;
    border-radius: 12px;
    margin: 15px 0;
    border-left: 5px solid #2d8659;
}

.soil-section {
    border-left-color: #8b7355;
}

.location-section {
    border-left-color: #ffc107;
}

.results-section {
    border-left-color: #2d8659;
}

.stButton>button {
    width: 100%;
    border-radius: 12px;
    height: 3.5em;
    background: linear-gradient(90deg, #2d8659, #1a4d2e) !important;
    color: white !important;
    font-size: 16px !important;
    font-weight: bold !important;
    border: 2px solid #1a4d2e !important;
    transition: all 0.3s ease;
}

.stButton>button:hover {
    background: linear-gradient(90deg, #1a4d2e, #2d8659) !important;
    box-shadow: 0 8px 20px rgba(45, 134, 89, 0.4);
    transform: translateY(-2px);
}

.card {
    background: white;
    padding: 20px;
    border-radius: 12px;
    margin: 15px 0;
    border: 2px solid #2d8659;
    box-shadow: 0 4px 15px rgba(45, 134, 89, 0.1);
}

.crop-card {
    background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
    padding: 20px;
    border-radius: 12px;
    margin: 10px 0;
    border-left: 5px solid #2d8659;
    text-align: center;
}

.crop-card h4 {
    color: #1a4d2e;
    font-size: 1.3em;
    margin-bottom: 10px;
}

.crop-card p {
    color: #2d8659;
    font-size: 1.1em;
    font-weight: bold;
}

.weather-card {
    background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    border: 2px solid #ffc107;
}

.npk-display {
    background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
    padding: 15px;
    border-radius: 10px;
    margin: 10px 0;
    font-weight: bold;
    color: #6a1b9a;
}

.login-container {
    max-width: 500px;
    margin: 50px auto;
    background: white;
    padding: 40px;
    border-radius: 15px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
    border-top: 5px solid #2d8659;
}

.login-title {
    text-align: center;
    color: #1a4d2e;
    font-size: 2em;
    margin-bottom: 30px;
}

.metric-card {
    background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
    padding: 20px;
    border-radius: 10px;
    text-align: center;
    border: 2px solid #1976d2;
    margin: 10px;
}

.metric-card h3 {
    color: #1565c0;
    font-size: 0.9em;
    margin: 0;
    border: none;
    padding: 0;
    margin-bottom: 10px;
}

.metric-card p {
    color: #1565c0;
    font-size: 1.8em;
    font-weight: bold;
    margin: 0;
}

.voice-button {
    background: linear-gradient(90deg, #ff6f00, #ff8f00) !important;
}

.voice-button:hover {
    background: linear-gradient(90deg, #ff8f00, #ff6f00) !important;
}

.recommendation-highlight {
    background: linear-gradient(135deg, #fff59d 0%, #ffee58 100%);
    padding: 20px;
    border-radius: 12px;
    border: 3px solid #fbc02d;
    text-align: center;
    font-size: 1.2em;
    color: #f57f17;
    font-weight: bold;
    margin: 20px 0;
}

.section-divider {
    border-top: 3px dashed #2d8659;
    margin: 25px 0;
    opacity: 0.5;
}

.input-label {
    color: #1a4d2e;
    font-weight: bold;
    margin-bottom: 8px;
    display: block;
}

.soil-info {
    background: #fff8e1;
    padding: 12px;
    border-radius: 8px;
    margin-top: 8px;
    font-size: 0.9em;
    color: #f57f17;
    border-left: 4px solid #fbc02d;
}
</style>
""", unsafe_allow_html=True)

# ---------- SESSION ----------
if "token" not in st.session_state:
    st.session_state.token = None
if "soil_data" not in st.session_state:
    st.session_state.soil_data = None

# ---------- VOICE ----------
def get_voice_input():
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            st.info("🎤 Listening... Speak your location")
            audio = r.listen(source, timeout=5)
        return r.recognize_google(audio)
    except Exception as e:
        st.error(f"Voice input failed: {str(e)}")
        return None

def speak(text):
    try:
        tts = gTTS(text, lang='en')
        tts.save("output.mp3")
        os.system("afplay output.mp3")
    except:
        pass

def fetch_soil_data(city, soil_type):
    """Fetch soil data from backend based on location and soil type"""
    try:
        response = requests.get(
            "http://127.0.0.1:5001/api/soil/data",
            params={"city": city, "soil_type": soil_type},
            headers={"Authorization": f"Bearer {st.session_state.token}"}
        )
        data = response.json()
        if data.get("success"):
            return data.get("data", {})
        return None
    except:
        return None

# ---------- AUTH ----------
st.markdown("""
<div class="header-container">
    <h1>🌾 KRISHI AI</h1>
    <p>Smart Crop Recommendation System</p>
    <p style="margin-top: 5px; font-size: 0.85em;">Right Crop. Better Yield. Sustainable Future</p>
</div>
""", unsafe_allow_html=True)

if st.session_state.token is None:
    st.markdown("""
    <div class="login-container">
        <h2 class="login-title">🔐 Login / Signup</h2>
    </div>
    """, unsafe_allow_html=True)

    username = st.text_input("👤 Username", placeholder="Enter your username")
    password = st.text_input("🔑 Password", type="password", placeholder="Enter your password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📝 Signup"):
            if username and password:
                res = requests.post(
                    "http://127.0.0.1:5001/api/auth/signup",
                    json={"username": username, "password": password}
                )
                data = res.json()
                if data.get("success"):
                    st.success("✅ Signup successful! Please login.")
                else:
                    st.error(f"❌ {data.get('message', 'Signup failed')}")
            else:
                st.warning("⚠️ Please enter username and password")

    with col2:
        if st.button("🚀 Login"):
            if username and password:
                res = requests.post(
                    "http://127.0.0.1:5001/api/auth/login",
                    json={"username": username, "password": password}
                )
                data = res.json()

                if data.get("success"):
                    st.session_state.token = data["token"]
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error(f"❌ {data.get('message', 'Login failed')}")
            else:
                st.warning("⚠️ Please enter username and password")

# ---------- MAIN APP ----------
else:
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🚪 Logout"):
            st.session_state.token = None
            st.session_state.soil_data = None
            st.rerun()

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    # LOCATION & SOIL SELECTION
    st.markdown("""
    <div class="location-section">
        <h2>📍 Soil & Location Details</h2>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        city = st.text_input("📍 Location / City", value="Delhi", help="Enter your city or region")

    with col2:
        soil = st.selectbox(
            "🌱 Soil Type",
            ["Loamy", "Sandy", "Clay", "Silt"],
            help="Select your primary soil type"
        )

    # VOICE INPUT
    st.markdown("<br>", unsafe_allow_html=True)
    col_voice_1, col_voice_2, col_voice_3 = st.columns([2, 1, 2])
    with col_voice_2:
        if st.button("🎤 Voice Input", key="voice_btn"):
            voice_text = get_voice_input()
            if voice_text:
                st.success(f"✅ Heard: {voice_text}")
                city = voice_text

    # FETCH SOIL DATA DYNAMICALLY
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="soil-section">
        <h2>🧪 Soil NPK Values</h2>
    </div>
    """, unsafe_allow_html=True)

    # Fetch soil data based on city and soil type
    soil_data = fetch_soil_data(city, soil)

    if soil_data:
        N = soil_data.get("N", 90)
        P = soil_data.get("P", 40)
        K = soil_data.get("K", 40)
        ph = soil_data.get("ph", 6.5)

        st.markdown(f"""
        <div class="npk-display">
            <p>Nitrogen (N): {N} mg/kg | Phosphorus (P): {P} mg/kg | Potassium (K): {K} mg/kg | pH: {ph}</p>
            <p style="font-size: 0.85em; margin-top: 8px;">📊 Based on {city} region and {soil} soil type</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Fallback to manual input
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            N = st.number_input("💚 Nitrogen (N)", 0, 140, 90, help="mg/kg")

        with col2:
            P = st.number_input("🟡 Phosphorus (P)", 0, 140, 40, help="mg/kg")

        with col3:
            K = st.number_input("💜 Potassium (K)", 0, 140, 40, help="mg/kg")

        with col4:
            ph = st.number_input("⚖️ pH Level", 0.0, 14.0, 6.5, step=0.1)

        st.markdown("""
        <div class="soil-info">
            💡 Soil data not found for this location. Using default values. Consider testing your soil for accurate recommendations.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    # ACTION BUTTONS
    col1, col2 = st.columns([2, 1])

    with col1:
        if st.button("🚀 Get Crop Recommendation", key="recommend_btn"):
            with st.spinner("🔍 Analyzing soil conditions..."):
                res = requests.post(
                    "http://127.0.0.1:5001/api/crop/recommend",
                    headers={"Authorization": f"Bearer {st.session_state.token}"},
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

                if data.get("success"):
                    speak(f"Recommended crop is {data['recommended_crop']}")

                    # MAIN RECOMMENDATION
                    st.markdown(f"""
                    <div class="recommendation-highlight">
                        🏆 Best Recommended Crop: <br>
                        <span style="font-size: 1.4em;">{data['recommended_crop']}</span>
                    </div>
                    """, unsafe_allow_html=True)

                    # TOP 3 CROPS
                    st.markdown("""
                    <div class="results-section">
                        <h2>🌾 Top 3 Recommended Crops</h2>
                    </div>
                    """, unsafe_allow_html=True)

                    crop_cols = st.columns(3)
                    for idx, item in enumerate(data.get("top_3", [])):
                        with crop_cols[idx]:
                            st.markdown(f"""
                            <div class="crop-card">
                                <h4>#{idx + 1} {item['crop']}</h4>
                                <p>{item['confidence'] * 100:.1f}% Match</p>
                            </div>
                            """, unsafe_allow_html=True)

                    # WEATHER INFO
                    st.markdown("""
                    <div class="section-divider"></div>
                    <div class="results-section">
                        <h2>🌦️ Weather & Environmental Conditions</h2>
                    </div>
                    """, unsafe_allow_html=True)

                    weather = data.get("weather", {})
                    w_col1, w_col2, w_col3, w_col4 = st.columns(4)

                    with w_col1:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h3>🌡️ Temperature</h3>
                            <p>{weather.get('temperature', 'N/A')}°C</p>
                        </div>
                        """, unsafe_allow_html=True)

                    with w_col2:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h3>💧 Humidity</h3>
                            <p>{weather.get('humidity', 'N/A')}%</p>
                        </div>
                        """, unsafe_allow_html=True)

                    with w_col3:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h3>☁️ Condition</h3>
                            <p>{weather.get('condition', 'N/A')}</p>
                        </div>
                        """, unsafe_allow_html=True)

                    with w_col4:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h3>🌍 Location</h3>
                            <p>{weather.get('city', city)}</p>
                        </div>
                        """, unsafe_allow_html=True)

                else:
                    st.error(f"❌ {data.get('message', 'Error getting recommendation')}")

    with col2:
        if st.button("📜 History", key="history_btn"):
            st.session_state.show_history = not st.session_state.get("show_history", False)

    # HISTORY
    if st.session_state.get("show_history", False):
        st.markdown("""
        <div class="section-divider"></div>
        <div class="results-section">
            <h2>📜 Your Recommendation History</h2>
        </div>
        """, unsafe_allow_html=True)

        with st.spinner("Loading history..."):
            res = requests.get(
                "http://127.0.0.1:5001/api/history/",
                headers={"Authorization": f"Bearer {st.session_state.token}"}
            )

            data = res.json()

            if data.get("success") and data.get("history"):
                for idx, item in enumerate(data["history"]):
                    st.markdown(f"""
                    <div class="card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <strong>📍 {item['input'].get('location', 'Unknown')}</strong><br>
                                <span style="color: #2d8659; font-weight: bold;">🌾 {item['result'][0]['crop']}</span><br>
                                <small style="color: #666;">Soil: {item['input'].get('soil', 'N/A')} | NPK: {item['input'].get('N')}-{item['input'].get('P')}-{item['input'].get('K')}</small>
                            </div>
                            <div style="text-align: right; font-size: 0.9em; color: #2d8659;">
                                Confidence: {item['result'][0]['confidence']*100:.1f}%
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("📭 No history yet. Start making recommendations!")
