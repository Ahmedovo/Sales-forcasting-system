from __future__ import annotations
from flask import Flask
from flask_cors import CORS
from .config import load_service_config
from .routes import auth_bp
from shared.metrics import create_metrics_blueprint


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)
    cfg = load_service_config()
    app.config["SERVICE_CONFIG"] = cfg

    # register blueprints
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(create_metrics_blueprint())
    return app
