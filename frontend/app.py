import streamlit as st
import requests
import speech_recognition as sr
from gtts import gTTS
import os

# ---------- CONFIG ----------
st.set_page_config(page_title="KRISHI AI", layout="centered")

# ---------- STYLE ----------
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #0f172a, #1e293b);
}
h1, h2, h3 {
    text-align: center;
    color: #22c55e;
}
.stButton>button {
    width: 100%;
    border-radius: 12px;
    height: 3em;
    background: linear-gradient(90deg, #22c55e, #16a34a);
    color: white;
    font-size: 16px;
}
.card {
    background: #111827;
    padding: 15px;
    border-radius: 12px;
    margin: 10px 0;
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
        st.info("🎤 Speak location...")
        audio = r.listen(source)

    try:
        return r.recognize_google(audio)
    except:
        return None

def speak(text):
    tts = gTTS(text)
    tts.save("output.mp3")
    os.system("afplay output.mp3")  # Mac

# ---------- AUTH ----------
st.title("🌾 KRISHI AI")

if st.session_state.token is None:
    st.subheader("🔐 Login / Signup")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Signup"):
            res = requests.post(
                "http://127.0.0.1:5001/api/auth/signup",
                json={"username": username, "password": password}
            )
            st.success(res.json()["message"])

    with col2:
        if st.button("Login"):
            res = requests.post(
                "http://127.0.0.1:5001/api/auth/login",
                json={"username": username, "password": password}
            )
            data = res.json()

            if data["success"]:
                st.session_state.token = data["token"]
                st.success("Login successful")
                st.rerun()
            else:
                st.error(data["message"])

# ---------- MAIN APP ----------
else:
    st.subheader("🌱 Smart Crop Recommendation")

    col1, col2 = st.columns(2)

    with col1:
        soil = st.selectbox("🌱 Soil", ["Loamy", "Sandy", "Clay"])
        N = st.number_input("Nitrogen", 0, 140, 90)
        P = st.number_input("Phosphorus", 0, 140, 40)

    with col2:
        city = st.text_input("📍 Location", "Delhi")
        K = st.number_input("Potassium", 0, 140, 40)
        ph = st.number_input("pH", 0.0, 14.0, 6.5)

    # 🎤 Voice
    if st.button("🎤 Speak Location"):
        voice_text = get_voice_input()
        if voice_text:
            st.success(f"You said: {voice_text}")
            city = voice_text

    # 🚀 Predict
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
                "ph": ph
            }
        )

        data = res.json()

        if data["success"]:
            st.success(f"🌾 Best Crop: {data['recommended_crop']}")

            speak(f"Recommended crop is {data['recommended_crop']}")

            st.markdown("### 🏆 Top 3")
            for item in data["top_3"]:
                st.write(f"{item['crop']} ({item['confidence']})")

            st.markdown("### 🌦 Weather")

            col1, col2, col3 = st.columns(3)
            col1.metric("Temp", f"{data['weather']['temperature']} °C")
            col2.metric("Humidity", f"{data['weather']['humidity']}%")
            col3.metric("Condition", data['weather']['condition'])

        else:
            st.error(data["message"])

    # 📜 HISTORY
    if st.button("📜 View History"):
        res = requests.get(
            "http://127.0.0.1:5001/api/history/",
            headers={"Authorization": f"Bearer {st.session_state.token}"}
        )

        data = res.json()

        if data["success"]:
            for item in data["history"]:
                st.markdown(f"""
                <div class="card">
                📍 {item['input']['location']} <br>
                🌱 {item['result'][0]['crop']}
                </div>
                """, unsafe_allow_html=True)