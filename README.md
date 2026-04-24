# 🌱 KRISHI AI Crop System

> Smart Agriculture Management System using **Flask, MongoDB, and Streamlit**  
> Built to help farmers manage farm data, user authentication, and weather insights.

---

## 🚀 Features

✨ Clean & Modular Backend  
🔐 Secure User Authentication (JWT)  
🌾 Farm Data Management System  
☁️ Weather API Integration (OpenWeather)  
📊 Interactive Streamlit Dashboard  
🗄️ MongoDB Atlas Cloud Storage  

---

## 🏗️ Project Structure

```bash
KRISHI-AI-Crop/
│
├── backend/
│   ├── controllers/
│   ├── models/
│   ├── routes/
│   ├── database/
│   ├── main.py
│   └── .env
│
├── frontend/
│   └── app.py
│
├── requirements.txt
└── README.md
🛠️ Tech Stack
Layer	Technology
Backend	Flask (Python)
Frontend	Streamlit
Database	MongoDB Atlas
Auth	JWT
API	OpenWeather API
⚙️ Setup Instructions
1️⃣ Clone Repository
git clone <your-repo-url>
cd KRISHI-AI-Crop-
2️⃣ Create Virtual Environment
python3 -m venv venv
source venv/bin/activate
3️⃣ Install Dependencies
pip install -r requirements.txt
🔐 Environment Variables

Create file: backend/.env

MONGO_URI=your_mongodb_connection_string 
/*YOU GOT ME*/
SECRET_KEY=your_secret_key
WEATHER_API_KEY=your_openweather_api_key
▶️ Run Application
🔹 Backend
cd backend
python3 main.py

Runs on:

http://127.0.0.1:5001
🔹 Frontend
cd frontend
streamlit run app.py
📡 API Endpoints
👤 User APIs
POST /api/user/signup
POST /api/user/login
🌾 Farm APIs
POST /api/farm/add
🌦️ Weather APIs
GET /api/weather/<city>
🧪 API Testing Example
curl -X POST http://127.0.0.1:5001/api/user/signup \
-H "Content-Type: application/json" \
-d '{"username":"test1","password":"1234"}'
📌 Future Enhancements

🚀 AI Crop Recommendation System
🧠 Disease Detection (ML)
📍 GPS-based Farm Mapping
📊 Advanced Analytics Dashboard

👨‍💻 Author

Harshit Kumar

⭐ Support

If you like this project, give it a ⭐ on GitHub!