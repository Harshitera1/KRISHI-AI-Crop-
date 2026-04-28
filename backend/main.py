import logging

from flask import Flask
from logging_config import configure_logging
from routes.user_routes import user_bp
from routes.farm_routes import farm_bp
from routes.weather_routes import weather_bp
from routes.crop_routes import crop_bp
from routes.fertilizer_routes import fertilizer_bp


configure_logging()
logger = logging.getLogger(__name__)

app = Flask(__name__)

app.register_blueprint(user_bp, url_prefix="/api/user")
app.register_blueprint(farm_bp, url_prefix="/api/farm")
app.register_blueprint(weather_bp, url_prefix="/api/weather")
app.register_blueprint(crop_bp, url_prefix="/api/crop")
app.register_blueprint(fertilizer_bp, url_prefix="/api/fertilizer")

@app.route("/")
def home():
    return {"msg": "Backend running 🚀"}

if __name__ == "__main__":
    logger.info(
        "Backend running",
        extra={"event": "app_startup", "status_code": 200}
    )
    app.run(debug=True, port=5001)
