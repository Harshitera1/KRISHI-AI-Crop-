from flask import Flask
from routes.user_routes import user_bp

from routes.farm_routes import farm_bp



app = Flask(__name__)

app.register_blueprint(user_bp, url_prefix="/api/user")
app.register_blueprint(farm_bp, url_prefix="/api/farm")
if __name__ == "__main__":
    print("🚀 Backend running...")
    app.run(debug=True, port=5001)