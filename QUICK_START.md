# ⚡ QUICK START GUIDE - KRISHI AI Enhanced

## 🚀 Installation & Setup

### 1️⃣ **Install New Dependencies**

```bash
# Navigate to project root
cd /Users/harshitkumar/Desktop/KRISHI/KRISHI-AI-Crop-

# Upgrade pip (important!)
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

**New packages added:**
- `streamlit-folium` - Interactive maps in Streamlit
- `folium` - Map library
- `geopy` - Geocoding (city name from coordinates)
- `babel` - Language/locale support

---

### 2️⃣ **Start Backend Server**

```bash
# Terminal 1 - Backend
cd backend

# Activate virtual environment
source ../venv/bin/activate

# Run Flask server
python main.py

# Expected output:
# * Running on http://127.0.0.1:5001
```

**Important:** Make sure MongoDB is running!

---

### 3️⃣ **Start Frontend Application**

```bash
# Terminal 2 - Frontend
cd frontend

# Run Streamlit app
streamlit run app.py

# Expected output:
# You can now view your Streamlit app in your browser.
# Local URL: http://localhost:8501
```

---

## 🎮 **Using the Application**

### First Time Setup:
1. **Signup**: Create a new account with username & password
2. **Login**: Enter your credentials
3. **Set Language**: Use sidebar to select English or हिंदी
4. **Welcome!** You're ready to get recommendations

### Getting Crop Recommendations:

```
📍 Step 1: Select Location
   └─ Click on the interactive map
   └─ System extracts: latitude, longitude, city name

🌱 Step 2: Choose Soil Type
   └─ Options: Loamy, Sandy, Clay, Silty, Peaty
   └─ NPK values auto-populate based on region

🎤 Step 3: (Optional) Use Voice Input
   └─ Click "🎤 Voice Input" button
   └─ Speak your input
   └─ Recommendation triggers automatically!

   OR

   🚀 Step 3: Get Recommendation Manually
   └─ Adjust N, P, K if needed (optional)
   └─ Click "🚀 Get Recommendation" button

✅ Step 4: View Results
   └─ Best crop recommendation
   └─ Top 3 alternatives
   └─ Region-specific NPK values
   └─ Fertilizer recommendations
```

---

## 🌐 **Features Overview**

### 📍 **Interactive Map**
- Real-time map selection
- Auto-detects city name
- Shows exact coordinates
- Reverse geocoding included

### 🗣️ **Voice Input**
- Speak naturally
- Auto-triggers recommendations
- No manual button click needed
- Supports English voice recognition

### 🌍 **Language Support**
- Switch between English & हिंदी (Hindi)
- All UI translates instantly
- Backend supports translations

### 📊 **Region-Based NPK**
- Varies by geographic location
- Supports 4 major regions of India
- Customized for each crop
- Based on soil and climate

### 🧪 **Smart Fertilizer Recommendations**
- Specific fertilizer types
- Exact dosages (kg/hectare)
- Region-specific values
- Detailed descriptions

### 🎨 **Premium UI**
- Modern gradient backgrounds
- Glass-morphism card design
- Smooth animations
- Responsive layout

---

## 🔍 **Testing the Features**

### Test Map Selection:
1. Login to the app
2. Look for "📍 Select Location on Map"
3. Click anywhere on the map
4. Verify location appears on right panel
5. Try clicking different cities

### Test Voice Input:
1. Ensure microphone is working
2. Click "🎤 Voice Input"
3. Speak: "Delhi loamy soil"
4. See recommendation auto-trigger
5. No need to click "Get Recommendation"

### Test Language Switching:
1. Get a recommendation in English
2. Go to sidebar settings
3. Switch to "हिंदी"
4. See all text change to Hindi
5. Switch back to verify

### Test NPK Values:
1. Select a location (e.g., Punjab)
2. Get recommendation for Wheat
3. Note NPK values shown
4. Change location to South India
5. Get Wheat recommendation again
6. See different NPK values for same crop!

### Test Fertilizer Info:
1. Get any crop recommendation
2. Scroll down to "🧪 Fertilizer Recommendation"
3. Verify shows:
   - Fertilizer type
   - NPK values for your region
   - Recommended dosage
   - Region information

---

## 📁 **Project Structure Changes**

```
KRISHI-AI-Crop-/
├── requirements.txt (UPDATED - new packages)
├── ENHANCED_FEATURES_GUIDE.md (NEW)
├── QUICK_START.md (NEW - this file)
│
├── frontend/
│   └── app.py (REWRITTEN - complete redesign)
│
├── backend/
│   ├── models/
│   │   └── npk_region_model.py (NEW - regional NPK database)
│   │
│   ├── services/
│   │   └── fertilizer_service.py (UPDATED - region-based NPK)
│   │
│   ├── controllers/
│   │   └── crop_controller.py (UPDATED - includes fertilizer)
│   │
│   └── utils/
│       └── translations.py (NEW - Hindi/English translations)
```

---

## 🐛 **Troubleshooting**

### Map Not Showing?
```
Error: "st_folium() got an unexpected keyword argument"
Solution:
  pip install --upgrade streamlit-folium folium
  streamlit run app.py --logger.level=debug
```

### Voice Recognition Not Working?
```
Error: "Could not request results from Google Speech Recognition"
Solution:
  1. Check internet connection
  2. Check microphone permissions
  3. Try speaking slowly and clearly
  4. Ensure no background noise
```

### Location Not Detected?
```
Error: "Could not reverse geocode coordinates"
Solution:
  1. Map might be zoomed too far
  2. Click in a more populated area
  3. Manually type city name in input
  4. Check internet connection
```

### Hindi Text Not Showing?
```
Error: "Mojibake or unreadable characters"
Solution:
  1. Streamlit auto-handles UTF-8, should work
  2. Try refreshing page (Cmd+Shift+R)
  3. Clear browser cache
  4. Use a modern browser (Chrome, Firefox, Safari)
```

### NPK Values Not Changing Between Regions?
```
Error: "Same NPK for different regions"
Solution:
  1. Ensure you're clicking on map to change location
  2. Backend needs to receive latitude/longitude
  3. Check browser console (F12) for errors
  4. Verify requests going to backend
```

### MongoDB Connection Error?
```
Error: "pymongo.errors.ConnectionFailure"
Solution:
  1. Start MongoDB: brew services start mongodb-community
  2. Check MongoDB running: brew services list
  3. Verify connection string in .env
  4. Restart backend server
```

---

## 🎯 **Key Features at a Glance**

| Feature | Before | After |
|---------|--------|-------|
| Location Input | Type city name | Click on interactive map |
| Voice Input | Requires manual confirmation | Auto-triggers recommendation |
| Languages | Only English | English + हिंदी + Extensible |
| NPK Adjustment | Global average | Region & crop specific |
| Fertilizer Info | Generic text | Detailed regional dosages |
| UI Design | Basic styling | Premium modern design |
| Mobile Friendly | Limited | Responsive layout |

---

## 💡 **Pro Tips**

1. **Better Map Selection**: Zoom in before clicking for precise location
2. **Faster Voice Input**: Speak clearly and pause between words
3. **Language Switching**: Switch before getting recommendations to see translated results
4. **NPK Exploration**: Try same crop in different regions to see differences
5. **Fertilizer Dosage**: Use recommended values as baseline, consult local agronomist
6. **History Tracking**: Check "📜 View History" to see past recommendations

---

## 📞 **Need Help?**

Check logs:
```bash
# Backend logs
tail -f backend.log

# Frontend logs
# Check browser console: F12 → Console tab

# Check specific errors
grep "ERROR" backend.log
```

---

## ✅ **Checklist Before Using**

- [ ] Python 3.8+ installed
- [ ] Virtual environment activated
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] MongoDB running
- [ ] Backend server started (port 5001)
- [ ] Frontend started (port 8501)
- [ ] Map loads without errors
- [ ] Can login/signup successfully
- [ ] Language switching works
- [ ] Microphone permission granted for voice input

---

## 🎉 **You're All Set!**

Your KRISHI AI application now has:
- ✅ Interactive map for location selection
- ✅ Voice input with auto-recommendation trigger
- ✅ Bilingual support (English & Hindi)
- ✅ Region-based NPK recommendations
- ✅ Smart fertilizer suggestions
- ✅ Premium modern UI design

**Ready to empower farmers!** 🌾🚜

---

**Last Updated**: April 30, 2026
**Version**: 2.0 (Enhanced with Maps, Voice, Language, and Regional NPK)
