from __future__ import annotations
from flask import Flask
from flask_cors import CORS
from .routes import forecast_bp
from shared.metrics import create_metrics_blueprint
from .consumer import start_consumer_thread


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)
    app.register_blueprint(forecast_bp, url_prefix="/api")
    app.register_blueprint(create_metrics_blueprint())

    # Start background consumer thread when app starts
    start_consumer_thread()
    return app
