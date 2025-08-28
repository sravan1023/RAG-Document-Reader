# --- load .env early ---
import os
from dotenv import load_dotenv

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
load_dotenv(os.path.join(PROJECT_ROOT, ".env"), override=True)
# --- end .env ---

from flask import Flask
from flask_cors import CORS
from app.api.routes import api_blueprint  # safe to import now

def create_app():
    app = Flask(__name__)
    CORS(app)  # or CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})
    app.register_blueprint(api_blueprint, url_prefix="/api")
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
