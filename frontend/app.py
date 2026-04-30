import streamlit as st
import requests
import speech_recognition as sr
from gtts import gTTS
import os
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import time
import plotly.express as px
import pandas as pd
from functools import lru_cache

# ---------- CONFIG ----------
st.set_page_config(page_title="KRISHI AI", layout="wide", initial_sidebar_state="expanded")

@st.cache_data
def get_translations():
    """Cache translations to improve performance"""
    return {
        "en": {
            "title": "🌾 KRISHI AI",
            "subtitle": "Smart Crop Recommendation System",
            "login_signup": "🔐 Login / Signup",
            "username": "Username",
            "password": "Password",
            "signup": "Signup",
            "login": "Login",
            "select_location": "📍 Select Location on Map",
            "soil_type": "🌱 Soil Type",
            "voice_input": "🎤 Voice Input",
            "get_recommendation": "🚀 Get Recommendation",
            "best_crop": "🌾 Best Crop",
            "top_crops": "🏆 Top 3 Crops",
            "weather": "🌦 Weather",
            "temperature": "🌡 Temperature",
            "humidity": "💧 Humidity",
            "condition": "☁ Condition",
            "history": "📜 View History",
            "nitrogen": "Nitrogen (N)",
            "phosphorus": "Phosphorus (P)",
            "potassium": "Potassium (K)",
            "fertilizer": "🧪 Fertilizer Recommendation",
            "region": "Region",
            "language": "Language",
            "confidence": "Confidence",
            "crop_yield": "📊 Expected Yield Comparison",
            "region_info": "🌍 Region Information",
            "city": "City",
            "soil": "Soil",
            "suitable_crops": "🌱 Suitable Crops",
            "location": "Location",
            "yield_per_hectare": "Yield per Hectare (tons/ha)",
            "speaking_language": "🔊 Speaking Language",
        },
        "hi": {
            "title": "🌾 कृषि एआई",
            "subtitle": "स्मार्ट फसल सिफारिश प्रणाली",
            "login_signup": "🔐 लॉगिन / साइन अप",
            "username": "उपयोगकर्ता नाम",
            "password": "पासवर्ड",
            "signup": "साइन अप",
            "login": "लॉगिन",
            "select_location": "📍 मानचित्र पर स्थान चुनें",
            "soil_type": "🌱 मिट्टी का प्रकार",
            "voice_input": "🎤 वॉइस इनपुट",
            "get_recommendation": "🚀 सिफारिश प्राप्त करें",
            "best_crop": "🌾 सर्वश्रेष्ठ फसल",
            "top_crops": "🏆 शीर्ष 3 फसलें",
            "weather": "🌦 मौसम",
            "temperature": "🌡 तापमान",
            "humidity": "💧 आर्द्रता",
            "condition": "☁ स्थिति",
            "history": "📜 इतिहास देखें",
            "nitrogen": "नाइट्रोजन (N)",
            "phosphorus": "फॉस्फोरस (P)",
            "potassium": "पोटेशियम (K)",
            "fertilizer": "🧪 खाद की सिफारिश",
            "region": "क्षेत्र",
            "language": "भाषा",
            "confidence": "आत्मविश्वास",
            "crop_yield": "📊 अपेक्षित उपज तुलना",
            "region_info": "🌍 क्षेत्र की जानकारी",
            "city": "शहर",
            "soil": "मिट्टी",
            "suitable_crops": "🌱 उपयुक्त फसलें",
            "location": "स्थान",
            "yield_per_hectare": "उपज प्रति हेक्टेयर (टन/हेक्टेयर)",
            "speaking_language": "🔊 बोलने की भाषा",
        }
    }

TRANSLATIONS = get_translations()

@st.cache_data
def get_crop_yields():
    """Cache crop yields to improve performance"""
    return {
        "wheat": 4.5,
        "rice": 5.2,
        "maize": 6.8,
        "sugarcane": 85,
        "potato": 25,
        "cotton": 1.5,
        "chickpea": 1.8,
        "mustard": 1.8,
        "jute": 3.2,
        "lentil": 1.9,
        "tobacco": 2.5,
        "soybean": 2.2,
        "gram": 1.6,
        "groundnut": 2.8,
        "pepper": 1.2,
        "coffee": 2.4,
        "coconut": 8.5,
        "mango": 12,
        "pomegranate": 9,
    }

CROP_YIELDS = get_crop_yields()

def t(key):
    """Translate key"""
    lang = st.session_state.get("language", "en")
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)

# ---------- PREMIUM STYLING ----------
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
    }
    
    .stApp {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #1a7e47 100%);
        background-attachment: fixed;
    }
    
    /* Modern Card Style */
    .card {
        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 15px;
        padding: 20px;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        margin: 15px 0;
        transition: all 0.3s ease;
    }
    
    .card:hover {
        box-shadow: 0 15px 40px rgba(34, 197, 94, 0.4);
        transform: translateY(-2px);
        border-color: rgba(34, 197, 94, 0.5);
    }
    
    /* Inputs */
    .stTextInput input, .stNumberInput input {
        background-color: rgba(255,255,255,0.12) !important;
        color: white !important;
        border: 2px solid rgba(34, 197, 94, 0.3) !important;
        border-radius: 12px !important;
        font-size: 15px !important;
        padding: 12px 15px !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput input:focus, .stNumberInput input:focus {
        border: 2px solid #22c55e !important;
        box-shadow: 0 0 15px rgba(34, 197, 94, 0.5) !important;
        background-color: rgba(255,255,255,0.15) !important;
    }
    
    /* Selectbox */
    .stSelectbox div {
        background-color: rgba(255,255,255,0.12) !important;
        color: white !important;
        border-radius: 12px !important;
        border: 2px solid rgba(34, 197, 94, 0.3) !important;
    }
    
    .stSelectbox span {
        color: white !important;
        font-weight: 500 !important;
    }
    
    /* Labels */
    label {
        color: #4ade80 !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 30px !important;
        font-size: 15px !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 15px rgba(34, 197, 94, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton button:hover {
        box-shadow: 0 8px 25px rgba(34, 197, 94, 0.5) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Titles */
    h1, h2, h3 {
        color: #4ade80 !important;
        text-shadow: 0 2px 10px rgba(0,0,0,0.4) !important;
    }
    
    h1 {
        font-size: 3.5em !important;
        margin: 20px 0 !important;
        font-weight: 800 !important;
    }
    
    /* Success/Error */
    .stSuccess {
        background-color: rgba(34, 197, 94, 0.15) !important;
        border: 1px solid rgba(34, 197, 94, 0.5) !important;
        border-radius: 10px !important;
    }
    
    .stError {
        background-color: rgba(239, 68, 68, 0.15) !important;
        border: 1px solid rgba(239, 68, 68, 0.5) !important;
        border-radius: 10px !important;
    }
    
    /* Metrics */
    .stMetric {
        background: rgba(255,255,255,0.05) !important;
        border-radius: 12px !important;
        padding: 15px !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------- SESSION ----------
if "token" not in st.session_state:
    st.session_state.token = None
if "language" not in st.session_state:
    st.session_state.language = "en"
if "voice_language" not in st.session_state:
    st.session_state.voice_language = "en"
if "location_selected" not in st.session_state:
    st.session_state.location_selected = False
if "selected_coords" not in st.session_state:
    st.session_state.selected_coords = None
if "auto_recommend" not in st.session_state:
    st.session_state.auto_recommend = False
if "current_recommendation_id" not in st.session_state:
    st.session_state.current_recommendation_id = None
if "voice_spoken" not in st.session_state:
    st.session_state.voice_spoken = False
if "results_displayed" not in st.session_state:
    st.session_state.results_displayed = False

# ---------- VOICE & LOCATION ----------
AVAILABLE_CITIES = {
    "delhi": {"lat": 28.7041, "lng": 77.1025},
    "punjab": {"lat": 31.1471, "lng": 74.8550},
    "haryana": {"lat": 29.0588, "lng": 77.0745},
    "uttar pradesh": {"lat": 26.8467, "lng": 80.9462},
    "bihar": {"lat": 25.0961, "lng": 85.3131},
    "west bengal": {"lat": 24.8355, "lng": 88.2635},
    "jharkhand": {"lat": 23.6102, "lng": 85.2799},
    "maharashtra": {"lat": 19.7515, "lng": 75.7139},
    "madhya pradesh": {"lat": 22.9375, "lng": 78.6553},
    "karnataka": {"lat": 15.3173, "lng": 75.7139},
    "tamil nadu": {"lat": 11.1271, "lng": 78.6569},
    "telangana": {"lat": 18.1124, "lng": 79.0193},
    "andhra pradesh": {"lat": 15.9129, "lng": 78.4855},
}

SOIL_TYPES = ["loamy", "sandy", "clay", "silty", "peaty"]

def extract_location_from_speech(text):
    """Extract location and soil type from spoken text"""
    text_lower = text.lower()
    detected_location = None
    detected_soil = None
    
    # Find location
    for city, coords in AVAILABLE_CITIES.items():
        if city in text_lower:
            detected_location = city
            break
    
    # Find soil type
    for soil in SOIL_TYPES:
        if soil in text_lower:
            detected_soil = soil.capitalize()
            break
    
    return detected_location, detected_soil

def get_voice_input():
    """Get voice input and automatically trigger recommendation"""
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            st.info("🎤 Listening... Say location (e.g., 'Delhi'), soil type (e.g., 'sandy'), and say 'recommend'")
            audio = r.listen(source, timeout=10)
        return r.recognize_google(audio)
    except:
        return None

def speak(text, language="en", recommendation_id=None):
    """Text to speech with language support - only speak once per recommendation"""
    try:
        # Check if already spoken for this recommendation
        if recommendation_id and st.session_state.get("current_recommendation_id") == recommendation_id and st.session_state.get("voice_spoken"):
            return  # Already spoken, don't repeat
        
        # Map language codes
        lang_code = "hi" if language == "hi" else "en"
        tts = gTTS(text, lang=lang_code, slow=False)
        tts.save("output.mp3")
        os.system("afplay output.mp3 &")  # Use background process
        
        # Mark as spoken for this recommendation
        if recommendation_id:
            st.session_state.voice_spoken = True
            st.session_state.current_recommendation_id = recommendation_id
    except Exception as e:
        print(f"Speech error: {e}")
        pass

def translate_crop_name(crop, language):
    """Translate crop names to Hindi"""
    crop_translations = {
        "wheat": "गेहूँ",
        "rice": "चावल",
        "maize": "मक्का",
        "sugarcane": "गन्ना",
        "potato": "आलू",
        "cotton": "कपास",
        "chickpea": "चना",
        "mustard": "सरसों",
        "jute": "जूट",
        "lentil": "दाल",
        "tobacco": "तंबाकू",
        "soybean": "सोयाबीन",
        "gram": "चना",
        "groundnut": "मूंगफली",
        "pepper": "काली मिर्च",
        "coffee": "कॉफी",
        "coconut": "नारियल",
        "mango": "आम",
        "pomegranate": "अनार",
    }
    
    if language == "hi":
        return crop_translations.get(crop.lower(), crop)
    return crop

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    lang = st.selectbox(t("language"), ["English", "हिंदी"])
    st.session_state.language = "en" if lang == "English" else "hi"
    
    if st.session_state.token:
        st.markdown("---")
        voice_lang = st.selectbox(t("speaking_language"), ["English 🇬🇧", "हिंदी 🇮🇳"])
        st.session_state.voice_language = "en" if voice_lang == "English 🇬🇧" else "hi"
        
        if st.button("🚪 Logout"):
            st.session_state.token = None
            st.rerun()

# ---------- HEADER ----------
st.markdown(f"""
<div style='text-align: center; margin: 30px 0;'>
    <h1>{t('title')}</h1>
    <p style='color: #a3e635; font-size: 18px;'>{t('subtitle')}</p>
</div>
""", unsafe_allow_html=True)

# ---------- AUTH ----------
if st.session_state.token is None:
    st.markdown(f"### {t('login_signup')}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        username = st.text_input(t("username"))
    
    with col2:
        password = st.text_input(t("password"), type="password")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button(f"✍️ {t('signup')}"):
            res = requests.post(
                "http://127.0.0.1:5001/api/auth/signup",
                json={"username": username, "password": password}
            )
            data = res.json()
            if data.get("success"):
                st.success("✅ Account created! Please login.")
            else:
                st.error(data.get("message"))
    
    with col2:
        if st.button(f"🔓 {t('login')}"):
            res = requests.post(
                "http://127.0.0.1:5001/api/auth/login",
                json={"username": username, "password": password}
            )
            data = res.json()
            
            if data.get("success"):
                st.session_state.token = data["token"]
                st.success("✅ Login successful!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ Login failed")

# ---------- MAIN APPLICATION ----------
else:
    st.markdown("---")
    
    # 📊 DASHBOARD SECTION
    st.markdown(f"### 📊 Dashboard")
    
    # Fetch recent recommendations
    try:
        history_res = requests.get(
            "http://127.0.0.1:5001/api/history/",
            headers={"Authorization": f"Bearer {st.session_state.token}"}
        )
        history_data = history_res.json()
        
        if history_data.get("success") and history_data.get("history"):
            history_list = history_data["history"][:5]  # Last 5
            
            # Create table data
            table_data = []
            for i, item in enumerate(history_list, 1):
                input_info = item.get("input", {})
                result = item.get("result", [{}])[0]
                
                table_data.append({
                    "S.No": i,
                    "Location": input_info.get("location", "N/A"),
                    "🌾 Crop": result.get("crop", "N/A").upper(),
                    "Confidence": f"{round(result.get('confidence', 0)*100, 1)}%",
                    "Soil": input_info.get("soil", "N/A"),
                    "N": input_info.get("N", 0),
                    "P": input_info.get("P", 0),
                    "K": input_info.get("K", 0),
                })
            
            # Display table
            import pandas as pd
            df = pd.DataFrame(table_data)
            
            st.markdown("""
            <div style='background: rgba(255,255,255,0.05); border-radius: 10px; padding: 15px; margin: 10px 0;'>
            """, unsafe_allow_html=True)
            
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("📭 No recommendations yet. Make your first recommendation!")
    except Exception as e:
        st.warning(f"Could not load dashboard: {str(e)}")
    
    st.markdown("---")
    
    # MAP & VOICE INPUT SECTION (INTEGRATED)
    st.markdown(f"### {t('select_location')}")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Initialize default location (Delhi)
        default_lat = 28.7041
        default_lng = 77.1025
        default_city = "Delhi"
        
        if st.session_state.selected_coords:
            default_lat = st.session_state.selected_coords["lat"]
            default_lng = st.session_state.selected_coords["lng"]
            default_city = st.session_state.selected_coords.get("city", "")
        
        # Create map
        m = folium.Map(
            location=[default_lat, default_lng],
            zoom_start=10,
            tiles="OpenStreetMap"
        )
        
        # Add marker for selected location
        if st.session_state.selected_coords:
            folium.Marker(
                location=[default_lat, default_lng],
                popup=f"📍 Selected: {default_city}",
                icon=folium.Icon(color="green", icon="check")
            ).add_to(m)
        
        # Streamlit map interaction
        map_data = st_folium(m, width=700, height=400)
        
        # ✅ AUTO-TRIGGER ON MAP CLICK - Match to nearest known city
        if map_data and map_data.get("last_clicked"):
            lat = map_data["last_clicked"]["lat"]
            lng = map_data["last_clicked"]["lng"]
            
            # Find nearest known city from database (most accurate for regions)
            import math
            min_distance = float('inf')
            nearest_city = "Unknown"
            
            for city_key, coords in AVAILABLE_CITIES.items():
                lat_diff = coords["lat"] - lat
                lng_diff = coords["lng"] - lng
                distance = math.sqrt(lat_diff**2 + lng_diff**2)
                
                if distance < min_distance:
                    min_distance = distance
                    nearest_city = city_key.title()
            
            st.session_state.selected_coords = {
                "lat": lat,
                "lng": lng,
                "city": nearest_city
            }
            
            st.success(f"✓ Location selected: {nearest_city} (Region-matched)")
            st.session_state.auto_recommend = True
            st.rerun()
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.session_state.selected_coords:
            lat = st.session_state.selected_coords["lat"]
            lng = st.session_state.selected_coords["lng"]
            city = st.session_state.selected_coords["city"]
            
            st.markdown(f"""
            <div class='card'>
            <h3>📍 Location</h3>
            <p><strong>City:</strong> {city}</p>
            <p><strong>Lat:</strong> {lat:.4f}</p>
            <p><strong>Lng:</strong> {lng:.4f}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("👆 Click map or use voice")
    
    # MAIN INPUT SECTION
    st.markdown("---")
    st.markdown("### 🌾 Crop Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    soil_types = ["Loamy", "Sandy", "Clay", "Silty", "Peaty"]
    
    with col1:
        soil = st.selectbox(t("soil_type"), soil_types)
    
    with col2:
        if st.button(f"🎤 {t('voice_input')} 🎤"):
            voice_text = get_voice_input()
            if voice_text:
                st.info(f"📢 You said: {voice_text}")
                
                # ✅ EXTRACT LOCATION & SOIL FROM SPEECH
                detected_location, detected_soil = extract_location_from_speech(voice_text)
                
                if detected_location:
                    # Find nearest city in database
                    detected_location_lower = detected_location.lower()
                    city_matched = None
                    
                    for city_key, coords in AVAILABLE_CITIES.items():
                        if detected_location_lower in city_key or city_key in detected_location_lower:
                            city_matched = city_key.title()
                            st.session_state.selected_coords = {
                                "lat": coords["lat"],
                                "lng": coords["lng"],
                                "city": city_matched
                            }
                            st.success(f"✅ Location matched: {city_matched}")
                            break
                    
                    if not city_matched:
                        st.warning(f"Could not find exact match for {detected_location}. Try a major city name.")
                else:
                    st.warning("Could not extract location from speech. Please try again with city name.")
                
                # Update soil if detected
                if detected_soil:
                    st.success(f"✅ Soil type detected: {detected_soil}")
                
                # Auto-trigger recommendation
                st.session_state.auto_recommend = True
                time.sleep(0.5)  # Small delay to ensure state is updated
                st.rerun()
            else:
                st.error("❌ Could not hear input. Please try again.")
    
    with col3:
        st.write("")
    
    # GET SOIL DATA
    N = P = K = ph = None
    city = st.session_state.selected_coords["city"] if st.session_state.selected_coords else "Delhi"
    
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
    except:
        pass
    
    # NPK INPUTS
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        N = st.number_input(t("nitrogen"), min_value=0, max_value=500, value=int(N) if N else 90)
    
    with col2:
        P = st.number_input(t("phosphorus"), min_value=0, max_value=500, value=int(P) if P else 40)
    
    with col3:
        K = st.number_input(t("potassium"), min_value=0, max_value=500, value=int(K) if K else 40)
    
    with col4:
        ph = st.number_input("pH Level", min_value=4.0, max_value=9.0, value=float(ph) if ph else 7.0, step=0.1)
    
    # GET WEATHER
    weather_data = {"temperature": 25, "humidity": 50, "condition": "Sunny"}
    try:
        w = requests.get(f"http://127.0.0.1:5001/api/weather/{city}")
        weather_data = w.json().get("weather", weather_data)
    except:
        pass
    
    # PREDICT BUTTON
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        predict_button = st.button(f"{t('get_recommendation')} 🚀", key="predict")
    
    # AUTO TRIGGER IF VOICE INPUT
    if st.session_state.auto_recommend:
        predict_button = True
        st.session_state.auto_recommend = False
    
    if predict_button:
        # Use selected location or default to Delhi
        if not st.session_state.selected_coords:
            st.session_state.selected_coords = {
                "lat": 28.7041,
                "lng": 77.1025,
                "city": "Delhi"
            }
            st.info("📍 Using default location: Delhi")
        
        lat = st.session_state.selected_coords["lat"]
        lng = st.session_state.selected_coords["lng"]
        
        res = requests.post(
            "http://127.0.0.1:5001/api/crop/recommend",
            headers={"Authorization": f"Bearer {st.session_state.token}"},
            json={
                "location": city,
                "latitude": lat,
                "longitude": lng,
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
            # Create unique ID for this recommendation (prevents duplicate speaking/display)
            rec_id = f"{city}_{data['recommended_crop']}_{time.time()}"
            st.session_state.current_recommendation_id = rec_id
            st.session_state.voice_spoken = False  # Reset voice spoken flag
            st.session_state.results_displayed = False
            
            # BEST CROP (only show if not already displayed)
            if not st.session_state.results_displayed:
                st.markdown("---")
                
                best_crop = data['recommended_crop'].title()
                best_crop_hi = translate_crop_name(data['recommended_crop'], "hi")
                
                st.markdown(f"""
                <div class='card' style='background: linear-gradient(135deg, rgba(34,197,94,0.2), rgba(34,197,94,0.1)); border: 2px solid #22c55e;'>
                <h2 style='text-align: center; font-size: 28px;'>{t('best_crop')}</h2>
                <h1 style='text-align: center; font-size: 48px; color: #4ade80;'>{best_crop}</h1>
                <p style='text-align: center; font-size: 20px; color: #a3e635;'>{best_crop_hi}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # 🔊 COMPREHENSIVE VOICE FEEDBACK (ONLY ONCE)
                voice_lang = st.session_state.voice_language
                
                if voice_lang == "hi":
                    recommendation_text = f"{best_crop_hi} फसल {city} के लिए सबसे अच्छी है। "
                else:
                    recommendation_text = f"Best crop for {city} is {best_crop}. "
                
                if data.get("fertilizer"):
                    fert = data["fertilizer"]
                    if voice_lang == "hi":
                        recommendation_text += f"खाद का प्रकार है {fert.get('fertilizer_type', 'NPK खाद')}। "
                        npk = fert.get('npk_values', {})
                        recommendation_text += f"प्रति हेक्टेयर {npk.get('N', 0)} किलोग्राम नाइट्रोजन, {npk.get('P', 0)} किलोग्राम फॉस्फोरस, और {npk.get('K', 0)} किलोग्राम पोटेशियम लगाएं।"
                    else:
                        recommendation_text += f"Use {fert.get('fertilizer_type', 'NPK fertilizer')}. "
                        npk = fert.get('npk_values', {})
                        recommendation_text += f"Apply {npk.get('N', 0)} kilograms of nitrogen, {npk.get('P', 0)} kilograms of phosphorus, and {npk.get('K', 0)} kilograms of potassium per hectare."
                
                # Speak only once using recommendation ID
                speak(recommendation_text, language=voice_lang, recommendation_id=rec_id)
                st.success("🔊 Recommendation spoken!")
                st.session_state.results_displayed = True
            
            # TOP 3 CROPS TABLE
            st.markdown(f"### {t('top_crops')}")
            
            crops_table_data = []
            for i, crop_data in enumerate(data["top_3"][:3], 1):
                crop_name = crop_data['crop']
                confidence = round(crop_data['confidence']*100, 1)
                yield_value = CROP_YIELDS.get(crop_name.lower(), 3.5)
                
                crops_table_data.append({
                    "🏆": f"#{i}",
                    "🌾 Crop": crop_name.title(),
                    "📊 Confidence": f"{confidence}%",
                    "📈 Expected Yield": f"{yield_value} tons/ha",
                    "🇭🇮 हिंदी": translate_crop_name(crop_name, "hi")
                })
            
            crops_df = pd.DataFrame(crops_table_data)
            st.dataframe(crops_df, use_container_width=True, hide_index=True)
            
            # YIELD COMPARISON CHART
            st.markdown(f"### {t('crop_yield')}")
            
            chart_data = []
            for crop_data in data["top_3"][:3]:
                crop_name = crop_data['crop'].title()
                yield_value = CROP_YIELDS.get(crop_data['crop'].lower(), 3.5)
                chart_data.append({"Crop": crop_name, "Yield (tons/ha)": yield_value})
            
            chart_df = pd.DataFrame(chart_data)
            
            fig = px.bar(
                chart_df, 
                x="Crop", 
                y="Yield (tons/ha)",
                title="Expected Yield Comparison",
                color="Yield (tons/ha)",
                color_continuous_scale="Greens",
                text_auto=True,
                labels={"Yield (tons/ha)": "Yield (tons/ha)"}
            )
            
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(30, 60, 114, 0.5)",
                font=dict(color="#4ade80", size=12),
                height=400,
                xaxis=dict(showgrid=False, color="#4ade80"),
                yaxis=dict(showgrid=True, gridcolor="rgba(74, 222, 128, 0.2)", color="#4ade80"),
                title=dict(font=dict(color="#4ade80", size=18))
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # WEATHER INFO
            st.markdown(f"### {t('weather')}")
            
            wcol1, wcol2, wcol3 = st.columns(3)
            wcol1.metric(t("temperature"), f"{weather_data.get('temperature')} °C", "🌡")
            wcol2.metric(t("humidity"), f"{weather_data.get('humidity')}%", "💧")
            wcol3.metric(t("condition"), weather_data.get("condition", "N/A"), "☁")
            
            # SOIL & REGION INFO
            st.markdown(f"### {t('region_info')}")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                <div class='card'>
                <h3>📍 Location Details</h3>
                <p><strong>{t('city')}:</strong> {city}</p>
                <p><strong>{t('soil')}:</strong> {soil}</p>
                <p><strong>{t('region')}:</strong> {data.get('soil_info', {}).get('region', 'Unknown')}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                suitable = data.get('soil_info', {}).get('suitable_crops', [])
                crops_list = ', '.join(suitable) if suitable else 'N/A'
                st.markdown(f"""
                <div class='card'>
                <h3>{t('suitable_crops')}</h3>
                <p>{crops_list}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # FERTILIZER RECOMMENDATION
            if data.get("fertilizer"):
                st.markdown("---")
                st.markdown(f"### {t('fertilizer')}")
                
                fert = data["fertilizer"]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    <div class='card'>
                    <h3>🧪 Type</h3>
                    <p style='font-size: 18px; color: #4ade80;'>{fert.get('fertilizer_type', 'N/A')}</p>
                    <p>{fert.get('description', '')}</p>
                    <p style='margin-top: 10px; font-size: 14px;'><strong>Region:</strong> {fert.get('region', 'N/A')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    npk = fert.get('npk_values', {})
                    st.markdown(f"""
                    <div class='card'>
                    <h3>📊 NPK Values (kg/ha)</h3>
                    <p style='font-size: 16px;'><span style='color: #4ade80;'>N:</span> {npk.get('N', 0)} kg/ha</p>
                    <p style='font-size: 16px;'><span style='color: #4ade80;'>P:</span> {npk.get('P', 0)} kg/ha</p>
                    <p style='font-size: 16px;'><span style='color: #4ade80;'>K:</span> {npk.get('K', 0)} kg/ha</p>
                    <p style='margin-top: 10px; font-size: 12px;'>{fert.get('dosage', '')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class='card' style='margin-top: 20px;'>
                <p><strong>Region:</strong> {fert.get('region', 'N/A')}</p>
                <p><strong>Dosage:</strong> {fert.get('dosage', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
        
        else:
            st.error(f"❌ {data.get('message')}")
    
    # HISTORY
    st.markdown("---")
    
    if st.button(f"{t('history')} 📜"):
        res = requests.get(
            "http://127.0.0.1:5001/api/history/",
            headers={"Authorization": f"Bearer {st.session_state.token}"}
        )
        
        data = res.json()
        
        if data.get("success") and data.get("history"):
            st.markdown(f"### {t('history')}")
            
            for item in data["history"][:10]:  # Show last 10
                st.markdown(f"""
                <div class='card'>
                <p>📍 <strong>{item['input'].get('location', 'N/A')}</strong></p>
                <p>🌾 <strong>{item['result'][0]['crop']}</strong> - {round(item['result'][0]['confidence']*100, 1)}%</p>
                <p style='color: #888; font-size: 12px;'>{item.get('timestamp', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("📭 No history found")