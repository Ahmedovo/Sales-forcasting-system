import os
from flask import Flask
from .extensions import db, jwt
from .routes.auth import auth_bp
from .routes.products import products_bp
from .routes.sales import sales_bp
from .routes.forecast import forecast_bp
from .routes.admin import admin_bp
from .routes.health import health_bp
from .scheduler import start_scheduler
from .models import User


def create_app() -> Flask:
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_URL', 'sqlite:///app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET', 'supersecret_dev_change_me')
    app.config['JWT_ALGORITHM'] = os.getenv('JWT_ALGORITHM', 'HS256')
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False

    db.init_app(app)
    jwt.init_app(app)

    # Enable CORS for direct frontend->backend calls
    try:
        from flask_cors import CORS
        CORS(app, resources={r"/api/*": {"origins": "*"}})
    except Exception:
        pass

    app.register_blueprint(health_bp, url_prefix='/api/health')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(products_bp, url_prefix='/api/products')
    app.register_blueprint(sales_bp, url_prefix='/api/sales')
    app.register_blueprint(forecast_bp, url_prefix='/api/forecast')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    with app.app_context():
        db.create_all()

    # Start weekly scheduler once app is created (Flask 3 removed before_first_request)
    start_scheduler()

    return app

