from __future__ import annotations
from flask import Flask
from flask_cors import CORS
from .routes import sales_bp
from shared.metrics import create_metrics_blueprint


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)
    app.register_blueprint(sales_bp, url_prefix="/api/sales")
    app.register_blueprint(create_metrics_blueprint())
    return app
