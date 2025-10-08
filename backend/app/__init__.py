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
        CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
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
        # Lightweight startup migration for 'sku' column and unique index (Postgres-safe, idempotent)
        try:
            from sqlalchemy import text
            engine = db.get_engine()
            with engine.begin() as conn:
                # Ensure column exists (Postgres supports IF NOT EXISTS)
                conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS sku varchar(100)"))
                # Backfill values to satisfy NOT NULL constraint when newly added
                conn.execute(text("UPDATE products SET sku = CONCAT('SKU-', id) WHERE sku IS NULL OR sku = ''"))
                # Enforce NOT NULL (safe if already set)
                conn.execute(text("ALTER TABLE products ALTER COLUMN sku SET NOT NULL"))
                # Ensure unique index exists
                conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS uq_products_sku ON products (sku)"))
                
                # Add missing columns to forecasts table
                conn.execute(text("ALTER TABLE forecasts ADD COLUMN IF NOT EXISTS lower_bound float"))
                conn.execute(text("ALTER TABLE forecasts ADD COLUMN IF NOT EXISTS upper_bound float"))
                conn.execute(text("ALTER TABLE forecasts ADD COLUMN IF NOT EXISTS forecast_date date"))
        except Exception:
            # Ignore on SQLite or non-Postgres engines
            pass

    # Start weekly scheduler once app is created (Flask 3 removed before_first_request)
    start_scheduler()
    
    # Train model on startup if there's data in the database
    from .training import train_now
    with app.app_context():
        train_now()

    return app