import streamlit as st
import requests
import speech_recognition as sr
from gtts import gTTS
import os
import folium
from streamlit_folium import st_folium
import time
import plotly.express as px
import pandas as pd
import math

# ============================================================================
# 🌾 KRISHI AI - Smart Crop Recommendation System (Fixed)
# ============================================================================

st.set_page_config(page_title="KRISHI AI", layout="wide", initial_sidebar_state="expanded")

# ============================================================================
# BRIGHT & SIMPLE STYLING (NO DARK COLORS)
# ============================================================================
st.markdown("""
<style>
    /* Main background - Bright cream */
    .stApp {
        background-color: #ffffff !important;
    }
    
    /* Main container */
    .main {
        background-color: #ffffff !important;
    }
    
    /* Input fields - White with green border */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > input {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #27ae60 !important;
        padding: 12px !important;
        font-size: 15px !important;
    }
    
    /* Input labels - Dark text */
    label {
        color: #000000 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }
    
    /* Buttons - Green */
    .stButton > button {
        background-color: #27ae60 !important;
        color: white !important;
        border: none !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        border-radius: 6px !important;
        width: 100% !important;
    }
    
    .stButton > button:hover {
        background-color: #229954 !important;
    }
    
    /* Titles */
    h1 { color: #27ae60 !important; }
    h2 { color: #27ae60 !important; }
    h3 { color: #000000 !important; }
    
    /* Text - Black */
    p { color: #000000 !important; }
    
    /* Cards/boxes */
    .card {
        background-color: #f0f8f0 !important;
        border: 2px solid #27ae60 !important;
        border-radius: 8px !important;
        padding: 20px !important;
        margin: 15px 0 !important;
    }
    
    /* Success messages */
    .stSuccess {
        background-color: #d4edda !important;
        border: 1px solid #28a745 !important;
        border-radius: 6px !important;
    }
    
    /* Error messages */
    .stError {
        background-color: #f8d7da !important;
        border: 1px solid #f5c6cb !important;
        border-radius: 6px !important;
    }
    
    /* Info messages */
    .stInfo {
        background-color: #d1ecf1 !important;
        border: 1px solid #0c5460 !important;
        border-radius: 6px !important;
    }
    
    /* Warning messages */
    .stWarning {
        background-color: #fff3cd !important;
        border: 1px solid #ffc107 !important;
        border-radius: 6px !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa !important;
    }
    
    /* Dataframes */
    .stDataFrame {
        background-color: #ffffff !important;
    }
    
    /* Metrics */
    .stMetric {
        background-color: #f0f8f0 !important;
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# TRANSLATIONS
# ============================================================================
@st.cache_data
def get_translations():
    return {
        "en": {
            "title": "🌾 KRISHI AI",
            "subtitle": "Smart Crop Recommendation System",
            "login": "Login",
            "signup": "Sign Up",
            "username": "Username",
            "password": "Password",
            "language": "Language",
            "voice_language": "Voice Language",
            "logout": "Logout",
            "dashboard": "Dashboard",
            "select_input_method": "Select How to Choose Location",
            "map_method": "📍 Use Map",
            "voice_method": "🎤 Say Location",
            "click_on_map": "Click on map to select your location",
            "soil_type": "Soil Type",
            "say_location": "Say location name (e.g., 'Delhi', 'Meerut', 'Punjab')",
            "nitrogen": "Nitrogen (N)",
            "phosphorus": "Phosphorus (P)",
            "potassium": "Potassium (K)",
            "ph_level": "pH Level",
            "get_recommendation": "Get Recommendation",
            "voice_input_btn": "🎤 Listen for Location",
            "best_crop": "🏆 Best Crop",
            "top_crops": "Top 3 Recommended Crops",
            "confidence": "Confidence",
            "yield": "Expected Yield",
            "weather": "Weather",
            "temperature": "Temperature",
            "humidity": "Humidity",
            "condition": "Condition",
            "fertilizer": "Fertilizer Recommendation",
            "history": "Your Recent Recommendations",
            "location": "Location",
            "soil": "Soil",
            "listening": "🎤 Listening...",
            "processing": "Processing...",
            "success": "✅ Success!",
            "error": "❌ Error",
            "try_again": "Try again",
        },
        "hi": {
            "title": "🌾 कृषि एआई",
            "subtitle": "स्मार्ट फसल सिफारिश प्रणाली",
            "login": "लॉगिन",
            "signup": "साइन अप",
            "username": "उपयोगकर्ता नाम",
            "password": "पासवर्ड",
            "language": "भाषा",
            "voice_language": "वॉइस भाषा",
            "logout": "लॉगआउट",
            "dashboard": "डैशबोर्ड",
            "select_input_method": "अपना स्थान कैसे चुनें",
            "map_method": "📍 मानचित्र",
            "voice_method": "🎤 बोलें",
            "click_on_map": "अपना स्थान चुनने के लिए मानचित्र पर क्लिक करें",
            "soil_type": "मिट्टी का प्रकार",
            "say_location": "स्थान का नाम बोलें (जैसे 'दिल्ली', 'मेरठ', 'पंजाब')",
            "nitrogen": "नाइट्रोजन (N)",
            "phosphorus": "फॉस्फोरस (P)",
            "potassium": "पोटेशियम (K)",
            "ph_level": "pH स्तर",
            "get_recommendation": "सिफारिश प्राप्त करें",
            "voice_input_btn": "🎤 स्थान सुनें",
            "best_crop": "🏆 सर्वश्रेष्ठ फसल",
            "top_crops": "शीर्ष 3 अनुशंसित फसलें",
            "confidence": "विश्वास",
            "yield": "अपेक्षित उपज",
            "weather": "मौसम",
            "temperature": "तापमान",
            "humidity": "आर्द्रता",
            "condition": "स्थिति",
            "fertilizer": "खाद की सिफारिश",
            "history": "आपकी हाल की सिफारिशें",
            "location": "स्थान",
            "soil": "मिट्टी",
            "listening": "🎤 सुन रहे हैं...",
            "processing": "प्रोसेस कर रहे हैं...",
            "success": "✅ सफल!",
            "error": "❌ त्रुटि",
            "try_again": "फिर से कोशिश करें",
        }
    }

TRANSLATIONS = get_translations()

@st.cache_data
def get_locations():
    return {
        "delhi": {"lat": 28.7041, "lng": 77.1025},
        "meerut": {"lat": 28.9845, "lng": 77.7064},
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

@st.cache_data
def get_crop_names_hi():
    return {
        "wheat": "गेहूँ", "rice": "चावल", "maize": "मक्का", "sugarcane": "गन्ना",
        "potato": "आलू", "cotton": "कपास", "chickpea": "चना", "mustard": "सरसों",
        "jute": "जूट", "lentil": "दाल", "tobacco": "तंबाकू", "soybean": "सोयाबीन",
        "gram": "चना", "groundnut": "मूंगफली", "pepper": "काली मिर्च", "coffee": "कॉफी",
        "coconut": "नारियल", "mango": "आम", "pomegranate": "अनार",
    }

@st.cache_data
def get_crop_yields():
    return {
        "wheat": 4.5, "rice": 5.2, "maize": 6.8, "sugarcane": 85,
        "potato": 25, "cotton": 1.5, "chickpea": 1.8, "mustard": 1.8,
        "jute": 3.2, "lentil": 1.9, "tobacco": 2.5, "soybean": 2.2,
        "gram": 1.6, "groundnut": 2.8, "pepper": 1.2, "coffee": 2.4,
        "coconut": 8.5, "mango": 12, "pomegranate": 9,
    }

@st.cache_data
def get_crop_profits():
    return {
        "wheat": 45000, "rice": 52000, "maize": 48000, "sugarcane": 65000,
        "potato": 35000, "cotton": 42000, "chickpea": 38000, "mustard": 40000,
        "jute": 32000, "lentil": 36000, "tobacco": 55000, "soybean": 39000,
        "gram": 37000, "groundnut": 44000, "pepper": 60000, "coffee": 70000,
        "coconut": 55000, "mango": 50000, "pomegranate": 52000,
    }

@st.cache_data
def get_region_best_crops():
    return {
        "delhi": {"crop": "wheat", "confidence": 0.92},
        "punjab": {"crop": "wheat", "confidence": 0.95},
        "haryana": {"crop": "rice", "confidence": 0.90},
        "uttar pradesh": {"crop": "sugarcane", "confidence": 0.88},
        "bihar": {"crop": "maize", "confidence": 0.87},
    }

LOCATIONS = get_locations()
CROP_HI = get_crop_names_hi()
YIELDS = get_crop_yields()
PROFITS = get_crop_profits()
REGION_CROPS = get_region_best_crops()

def t(key):
    lang = st.session_state.get("language", "en")
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)

def find_nearest_location(lat, lng):
    min_dist = float('inf')
    nearest = "delhi"
    for city_key, coords in LOCATIONS.items():
        dist = math.sqrt((coords["lat"] - lat)**2 + (coords["lng"] - lng)**2)
        if dist < min_dist:
            min_dist = dist
            nearest = city_key
    return nearest

def match_voice_location(text):
    if not text:
        return None
    text_lower = text.lower()
    for city_key in LOCATIONS.keys():
        if city_key in text_lower or text_lower in city_key:
            return city_key
    return None

def translate_crop(crop, lang):
    if lang == "hi":
        return CROP_HI.get(crop.lower(), crop)
    return crop

def speak_output(text, language="en"):
    try:
        lang_code = "hi" if language == "hi" else "en"
        tts = gTTS(text, lang=lang_code, slow=False)
        tts.save("output.mp3")
        os.system("afplay output.mp3 2>/dev/null &")
    except:
        pass

def get_voice_input():
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            audio = r.listen(source, timeout=10)
        return r.recognize_google(audio)
    except:
        return None

# ============================================================================
# SESSION STATE
# ============================================================================
if "token" not in st.session_state:
    st.session_state.token = None
if "language" not in st.session_state:
    st.session_state.language = "en"
if "voice_language" not in st.session_state:
    st.session_state.voice_language = "en"
if "selected_location" not in st.session_state:
    st.session_state.selected_location = None
if "voice_input_text" not in st.session_state:
    st.session_state.voice_input_text = None

# ============================================================================
# SIDEBAR
# ============================================================================
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
    lang = st.selectbox(t("language"), ["English", "हिंदी"], key="lang_select")
    st.session_state.language = "en" if lang == "English" else "hi"
    
    if st.session_state.token:
        st.markdown("---")
        voice_lang = st.selectbox(t("voice_language"), ["English", "हिंदी"], key="voice_lang")
        st.session_state.voice_language = "en" if voice_lang == "English" else "hi"
        
        if st.button("🚪 " + t("logout")):
            st.session_state.token = None
            st.rerun()

# ============================================================================
# HEADER
# ============================================================================
st.markdown(f"# {t('title')}")
st.markdown(f"<h3 style='color: #27ae60; text-align: center;'>{t('subtitle')}</h3>", unsafe_allow_html=True)
st.markdown("---")

# ============================================================================
# AUTH
# ============================================================================
if st.session_state.token is None:
    st.markdown(f"## {t('login')} / {t('signup')}")
    
    col1, col2 = st.columns(2)
    with col1:
        username = st.text_input(t("username"))
    with col2:
        password = st.text_input(t("password"), type="password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button(f"✍️ {t('signup')}"):
            if not username or not password:
                st.error("Please enter both username and password")
            else:
                try:
                    res = requests.post("http://127.0.0.1:5001/api/auth/signup", json={"username": username, "password": password}, timeout=5)
                    res_data = res.json()
                    if res_data.get("success"):
                        st.success(t("success"))
                    else:
                        st.error(res_data.get("message", "Signup failed"))
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to backend. Make sure backend is running on port 5001")
                except requests.exceptions.Timeout:
                    st.error("❌ Backend request timed out")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    with col2:
        if st.button(f"🔓 {t('login')}"):
            if not username or not password:
                st.error("Please enter both username and password")
            else:
                try:
                    res = requests.post("http://127.0.0.1:5001/api/auth/login", json={"username": username, "password": password}, timeout=5)
                    res_data = res.json()
                    if res_data.get("success"):
                        st.session_state.token = res_data["token"]
                        st.success(t("success"))
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(res_data.get("message", "Login failed"))
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to backend. Make sure backend is running on port 5001")
                except requests.exceptions.Timeout:
                    st.error("❌ Backend request timed out")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# ============================================================================
# MAIN APP
# ============================================================================
else:
    st.markdown("---")
    
    # Dashboard - Show best crops for major regions
    st.markdown(f"## 📊 {t('dashboard')}")
    
    # Add regional crop recommendations table
    st.markdown("### 🌾 Best Crops by Region")
    region_data = []
    for region_name, region_info in REGION_CROPS.items():
        crop = region_info["crop"]
        confidence = round(region_info["confidence"] * 100, 1)
        profit = PROFITS.get(crop.lower(), 40000)
        region_data.append({
            "📍 Region": region_name.title(),
            "🌾 Best Crop": crop.title(),
            "📊 Confidence": f"{confidence}%",
            "💰 Est. Profit/Ha": f"₹{profit:,}"
        })
    st.dataframe(pd.DataFrame(region_data), use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # History
    try:
        res = requests.get("http://127.0.0.1:5001/api/history/", headers={"Authorization": f"Bearer {st.session_state.token}"})
        if res.json().get("success") and res.json().get("history"):
            st.markdown("### 📋 Your Recent Recommendations")
            data = []
            for i, item in enumerate(res.json()["history"][:5], 1):
                inp = item.get("input", {})
                out = item.get("result", [{}])[0]
                crop = out.get("crop", "").lower()
                conf = round(out.get('confidence', 0)*100)
                profit = PROFITS.get(crop, 40000)
                data.append({"#": i, t("location"): inp.get("location"), "🌾": out.get("crop", "").title(), t("confidence"): f"{conf}%", "💰 Profit": f"₹{profit:,}"})
            st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
        else:
            st.info("No recommendations yet")
    except:
        st.warning("Could not load history")
    
    st.markdown("---")
    
    # Input method
    st.markdown(f"## {t('select_input_method')}")
    input_method = st.radio("", options=["map", "voice"], format_func=lambda x: t("map_method") if x == "map" else t("voice_method"), horizontal=True, key="method")
    
    # MAP FLOW
    if input_method == "map":
        st.markdown(f"### {t('click_on_map')}")
        
        lat, lng = 28.7041, 77.1025
        if st.session_state.selected_location and st.session_state.selected_location in LOCATIONS:
            lat = LOCATIONS[st.session_state.selected_location]["lat"]
            lng = LOCATIONS[st.session_state.selected_location]["lng"]
        
        m = folium.Map(location=[lat, lng], zoom_start=5, tiles="OpenStreetMap")
        
        if st.session_state.selected_location and st.session_state.selected_location in LOCATIONS:
            folium.Marker(location=[LOCATIONS[st.session_state.selected_location]["lat"], LOCATIONS[st.session_state.selected_location]["lng"]], popup="Selected", icon=folium.Icon(color="green")).add_to(m)
        
        map_data = st_folium(m, width=1350, height=450)
        
        if map_data and map_data.get("last_clicked"):
            nearest = find_nearest_location(map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"])
            st.session_state.selected_location = nearest
            st.success(f"✓ {nearest.title()}")
            time.sleep(0.5)
            st.rerun()
    
    # VOICE FLOW
    else:
        st.markdown(f"### {t('say_location')}")
        if st.button(f"🎤 {t('voice_input_btn')}", use_container_width=True):
            with st.spinner(t("listening")):
                voice_text = get_voice_input()
            
            if voice_text:
                st.info(f"📢 {voice_text}")
                matched = match_voice_location(voice_text)
                
                if matched:
                    # Exact or partial match found
                    st.session_state.selected_location = matched
                    st.success(f"✓ {matched.title()}")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    # No exact match - find nearest location and store both
                    matched_location = None
                    min_dist = float('inf')
                    
                    # Check if voice input is a partial match with any location
                    voice_lower = voice_text.lower()
                    for location_key in LOCATIONS.keys():
                        if voice_lower in location_key or location_key in voice_lower:
                            matched_location = location_key
                            break
                    
                    if matched_location:
                        st.session_state.selected_location = matched_location
                        st.success(f"✓ {matched_location.title()}")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        # Voice location not recognized - find nearest from map center
                        default_lat, default_lng = 28.7041, 77.1025  # Delhi center
                        nearest = find_nearest_location(default_lat, default_lng)
                        st.session_state.selected_location = nearest
                        st.warning(f"Location '{voice_text}' not found. Using nearest: {nearest.title()}")
                        st.session_state.voice_input_text = voice_text  # Store original voice input
                        time.sleep(0.5)
                        st.rerun()
            else:
                st.error(t("error"))
    
    st.markdown("---")
    
    # Crop analysis
    st.markdown("## 🌾 Crop Analysis")
    
    if st.session_state.selected_location:
        city = st.session_state.selected_location
        st.success(f"📍 Selected: {city.title()}")
    else:
        st.warning("Select a location first")
        city = "delhi"
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        soil = st.selectbox(t("soil_type"), ["Loamy", "Sandy", "Clay", "Silty", "Peaty"])
    with col2:
        N = st.number_input(t("nitrogen"), 0, 500, 90)
    with col3:
        P = st.number_input(t("phosphorus"), 0, 500, 40)
    with col4:
        K = st.number_input(t("potassium"), 0, 500, 40)
    
    col1, col2 = st.columns(2)
    with col1:
        ph = st.number_input(t("ph_level"), 4.0, 9.0, 7.0, 0.1)
    with col2:
        st.write("")
    
    # Get weather using latitude and longitude for accuracy
    weather = {"temperature": 25, "humidity": 50, "condition": "Clear"}
    try:
        if st.session_state.selected_location and st.session_state.selected_location in LOCATIONS:
            coords = LOCATIONS[st.session_state.selected_location]
            # Try to get weather by city name first
            w = requests.get(f"http://127.0.0.1:5001/api/weather/{st.session_state.selected_location}")
            if w.status_code == 200:
                w_data = w.json()
                if w_data.get("success"):
                    weather = w_data.get("weather", weather)
    except:
        pass
    
    # Predict
    if st.button(f"🚀 {t('get_recommendation')}", use_container_width=True):
        st.markdown("---")
        
        with st.spinner(t("processing")):
            try:
                if not st.session_state.selected_location:
                    st.session_state.selected_location = "delhi"
                
                # Store the SELECTED location (user's choice on map or voice)
                user_selected_location = st.session_state.selected_location
                
                # If user input text from voice, use that for voice output
                voice_input_name = st.session_state.voice_input_text if st.session_state.voice_input_text else user_selected_location
                
                city = st.session_state.selected_location
                coords = LOCATIONS.get(city, LOCATIONS["delhi"])
                
                res = requests.post(
                    "http://127.0.0.1:5001/api/crop/recommend",
                    headers={"Authorization": f"Bearer {st.session_state.token}"},
                    json={"location": city.title(), "latitude": coords["lat"], "longitude": coords["lng"], "soil": soil, "N": N, "P": P, "K": K, "ph": ph, "temperature": weather.get("temperature", 25), "humidity": weather.get("humidity", 50), "rainfall": 100}
                )
                
                data = res.json()
                
                if data.get("success"):
                    best_crop = data["recommended_crop"]
                    best_crop_hi = translate_crop(best_crop, "hi")
                    profit = PROFITS.get(best_crop.lower(), 40000)
                    
                    # Get backend-mapped location (nearest to user selection)
                    backend_mapped_location = data.get("mapped_location", user_selected_location)
                    
                    # Get fertilizer info
                    fert = data.get("fertilizer", {})
                    npk_vals = fert.get("npk_values", {})
                    n = npk_vals.get("N", 100)
                    p = npk_vals.get("P", 50)
                    k = npk_vals.get("K", 40)
                    fert_type = fert.get("fertilizer_type", "NPK Fertilizer")
                    
                    # ========== VOICE OUTPUT ==========
                    # Voice announces: location is [USER SELECTED/SPOKEN], crop is X, fertilizers are Y
                    # (or mapped location if user selected from map and it differs)
                    v_lang = st.session_state.voice_language
                    
                    # Use voice input name if available (for unmapped voice locations)
                    display_location_name = voice_input_name if voice_input_name else user_selected_location
                    
                    if v_lang == "hi":
                        fert_text_hi = f"{n} किलोग्राम नाइट्रोजन, {p} किलोग्राम फॉस्फोरस और {k} किलोग्राम पोटेशियम"
                        voice_text = f"स्थान: {display_location_name.title()}। सर्वश्रेष्ठ फसल: {best_crop_hi}। खाद: {fert_type}। {fert_text_hi} प्रति हेक्टेयर।"
                    else:
                        voice_text = f"Location: {display_location_name.title()}. Best crop: {best_crop}. Fertilizer: {fert_type}. Use {n} kg Nitrogen, {p} kg Phosphorus and {k} kg Potassium per hectare."
                    
                    speak_output(voice_text, v_lang)
                    st.success("🔊 Voice output played")
                    
                    # Clear voice input text for next recommendation
                    st.session_state.voice_input_text = None
                    
                    # ========== DISPLAY CARD ==========
                    # Show what user selected, but note if it's mapped
                    is_location_mapped = backend_mapped_location.lower() == user_selected_location.lower()
                    
                    if is_location_mapped:
                        location_note = f"<p style='text-align: center; font-size: 14px; color: #229954;'><strong>✓ Location Found in Database</strong></p>"
                    else:
                        location_note = f"<p style='text-align: center; font-size: 13px; color: #666;'><strong>📍 Searching... Mapped to: {backend_mapped_location.title()}</strong></p>"
                    
                    st.markdown(f"""
                    <div class='card'>
                    <h2 style='text-align: center;'>{t('best_crop')}</h2>
                    <h1 style='text-align: center; color: #27ae60;'>{best_crop.upper()}</h1>
                    <p style='text-align: center; font-size: 18px;'>{best_crop_hi}</p>
                    <p style='text-align: center; font-size: 16px; color: #229954;'><strong>📍 {user_selected_location.title()}</strong></p>
                    {location_note}
                    <p style='text-align: center; font-size: 15px; color: #27ae60;'><strong>💰 Est. Profit: ₹{profit:,}/ha</strong></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Top 3 crops
                    st.markdown(f"## {t('top_crops')}")
                    crops_data = []
                    for i, crop_item in enumerate(data.get("top_3", [])[:3], 1):
                        crop_name = crop_item["crop"]
                        confidence = round(crop_item["confidence"] * 100, 1)
                        yield_val = YIELDS.get(crop_name.lower(), 3.5)
                        profit_val = PROFITS.get(crop_name.lower(), 40000)
                        crops_data.append({"🏆": i, "🌾": crop_name.title(), t("confidence"): f"{confidence}%", t("yield"): f"{yield_val} tons/ha", "💰 Profit": f"₹{profit_val:,}"})
                    
                    st.dataframe(pd.DataFrame(crops_data), use_container_width=True, hide_index=True)
                    
                    # Chart
                    st.markdown("## 📊 Yield Comparison")
                    chart_data = []
                    for crop_item in data.get("top_3", [])[:3]:
                        chart_data.append({"Crop": crop_item["crop"].title(), "Yield": YIELDS.get(crop_item["crop"].lower(), 3.5)})
                    
                    fig = px.bar(pd.DataFrame(chart_data), x="Crop", y="Yield", color_discrete_sequence=["#27ae60"], text_auto=True)
                    fig.update_layout(showlegend=False, hovermode=False, plot_bgcolor="#ffffff", paper_bgcolor="#ffffff", font=dict(color="#000000"))
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Fertilizer with voice explanation
                    if data.get("fertilizer"):
                        st.markdown("## 🧪 " + t("fertilizer"))
                        fert = data["fertilizer"]
                        
                        st.info(f"**Type:** {fert.get('fertilizer_type')}\n\n**Dosage:** {fert.get('dosage')}")
                    
                    # ========== WEATHER - Fetch for backend-mapped location ==========
                    st.markdown("## ☀️ " + t("weather"))
                    
                    # Fetch weather for backend-mapped location (nearest in database)
                    mapped_weather = {"temperature": 25, "humidity": 50, "condition": "Clear"}
                    try:
                        w = requests.get(f"http://127.0.0.1:5001/api/weather/{backend_mapped_location}")
                        if w.status_code == 200:
                            w_data = w.json()
                            if w_data.get("success"):
                                mapped_weather = w_data.get("weather", mapped_weather)
                    except:
                        pass
                    
                    st.markdown(f"**📍 Selected:** {user_selected_location.title()} | **📍 Mapped to:** {backend_mapped_location.title()}")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(t("temperature"), f"{mapped_weather.get('temperature', 'N/A')}°C")
                    with col2:
                        st.metric(t("humidity"), f"{mapped_weather.get('humidity', 'N/A')}%")
                    with col3:
                        st.metric(t("condition"), mapped_weather.get('condition', 'N/A'))
                
                else:
                    st.error(data.get("message", t("error")))
            
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to backend. Make sure backend is running on port 5001")
            except requests.exceptions.Timeout:
                st.error("❌ Backend request timed out. Please try again.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

st.markdown("---")
st.markdown("<p style='text-align: center; color: #27ae60;'>🌾 KRISHI AI | Powered by ML & Weather Data</p>", unsafe_allow_html=True)
