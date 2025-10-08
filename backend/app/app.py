from . import create_app  # keep file to avoid editor confusion; app now via factory

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import os
from datetime import datetime, timedelta
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import numpy as np
import threading
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configure the app
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_URL', 'postgresql+psycopg2://postgres:postgres@postgres:5432/postgres')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET', 'supersecret_dev_change_me')
app.config['JWT_ALGORITHM'] = os.getenv('JWT_ALGORITHM', 'HS256')
app.config['DEBUG'] = os.getenv('DEBUG', 'false').lower() == 'true'

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)

# Define model training function
def train_models():
    with app.app_context():
        print("Starting model training...")
        logger.info("Starting model training...")
        
        # Get all products
        products = Product.query.all()
        
        for product in products:
            # Get sales data for this product
            sales = Sale.query.filter_by(product_id=product.id).all()
            
            if len(sales) < 5:  # Need minimum data points
                continue
                
            # Prepare data for training
            dates = [sale.sale_date for sale in sales]
            quantities = [sale.quantity for sale in sales]
            
            # Convert to DataFrame for easier processing
            df = pd.DataFrame({
                'date': dates,
                'quantity': quantities
            })
            
            # Sort by date
            df = df.sort_values('date')
            
            # Simple linear regression model
            X = np.array(range(len(df))).reshape(-1, 1)
            y = df['quantity'].values
            
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X, y)
            
            # Predict next 4 weeks
            future_X = np.array(range(len(df), len(df) + 4)).reshape(-1, 1)
            predictions = model.predict(future_X)
            
            # Save predictions
            current_date = datetime.now().date()
            
            # Record model training
            training = ModelTraining(
                product_id=product.id,
                training_date=current_date,
                accuracy=model.score(X, y)
            )
            db.session.add(training)
            
            # Save forecasts
            for i, pred in enumerate(predictions):
                forecast_date = current_date + timedelta(days=7 * (i + 1))
                
                # Check if forecast already exists
                existing = Forecast.query.filter_by(
                    product_id=product.id,
                    forecast_date=forecast_date
                ).first()
                
                if existing:
                    existing.quantity = max(0, int(pred))
                else:
                    forecast = Forecast(
                        product_id=product.id,
                        forecast_date=forecast_date,
                        quantity=max(0, int(pred))
                    )
                    db.session.add(forecast)
        
        db.session.commit()
        logger.info("Model training completed")
        return True

# Import models after db initialization to avoid circular imports
from .models import User, Product, Sale, Forecast, ModelTraining
import pandas as pd
import io
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from werkzeug.utils import secure_filename

# Authentication routes
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    # Support either email or username, prefer email like the frontend
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')
    
    user = None
    if email:
        user = User.query.filter_by(email=email).first()
    elif username:
        user = User.query.filter_by(username=username).first()
    
    if user and user.password_hash == password:  # In production, use proper password hashing
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200
    
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 400
    
    new_user = User(username=username, email=email, password_hash=password)  # In production, hash the password
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({
        'id': user.id,
        'name': user.username,
        'email': user.email,
        'role': 'user'
    }), 200

# Product routes
@app.route('/api/products', methods=['GET'])
@jwt_required()
def get_products():
    products = Product.query.all()
    result = []
    for product in products:
        result.append({
            'id': str(product.id),
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'stock': product.stock
        })
    return jsonify({"items": result, "total": len(result)}), 200

@app.route('/api/products', methods=['POST'])
@jwt_required()
def create_product():
    data = request.get_json()
    new_product = Product(
        name=data.get('name'),
        description=data.get('description', ''),
        price=data.get('price'),
        stock=data.get('stock', 0)
    )
    db.session.add(new_product)
    db.session.commit()
    
    return jsonify({
        'id': str(new_product.id),
        'name': new_product.name,
        'description': new_product.description,
        'price': new_product.price,
        'stock': new_product.stock
    }), 201
    
@app.route('/api/products/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json()
    
    product.name = data.get('name', product.name)
    product.description = data.get('description', product.description)
    product.price = data.get('price', product.price)
    product.stock = data.get('stock', product.stock)
    
    db.session.commit()
    
    return jsonify({
        'id': str(product.id),
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'stock': product.stock
    }), 200
    
@app.route('/api/products/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    
    return jsonify({"message": "Product deleted successfully"}), 200

# CSV Upload and Processing
@app.route('/api/upload/csv', methods=['POST'])
@jwt_required()
def upload_csv():
    print("CSV upload endpoint called")
    if 'file' not in request.files:
        print("Error: No file part in request")
        return jsonify({"error": "No file part"}), 400
        
    file = request.files['file']
    if file.filename == '':
        print("Error: No file selected")
        return jsonify({"error": "No file selected"}), 400
        
    if file and '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() == 'csv':
        # Read CSV file
        print(f"Processing CSV file: {file.filename}")
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_data = pd.read_csv(stream)
        print(f"CSV data loaded, columns: {list(csv_data.columns)}")
        
        # Check if CSV has required columns
        required_columns = ['name', 'sku', 'product price', 'stock', 'quantity sale', 'date of sale']
        missing_columns = [col for col in required_columns if col not in csv_data.columns]
        
        if missing_columns:
            print(f"Error: Missing columns: {missing_columns}")
            return jsonify({"error": f"Missing columns: {', '.join(missing_columns)}"}), 400
            
        # Process the data
        products_created = 0
        sales_created = 0
        
        # Group by product info
        product_groups = csv_data.groupby(['name', 'sku', 'product price', 'stock'])
        
        for (name, sku, price, stock), group in product_groups:
            # Check if product exists by SKU (prevents redundancy)
            product = Product.query.filter_by(sku=sku).first()
            
            if not product:
                # Create new product
                product = Product(
                    name=name,
                    sku=sku,
                    price=float(price),
                    stock=int(stock),
                    description=''
                )
                db.session.add(product)
                db.session.flush()  # Get the product ID without committing
                products_created += 1
            else:
                # Update existing product with latest stock information
                product.stock = int(stock)
            
            # Process sales for this product
            for _, row in group.iterrows():
                try:
                    sale_date = pd.to_datetime(row['date of sale']).date()
                    
                    # Validate quantity is positive
                    quantity = int(row['quantity sale'])
                    if quantity <= 0:
                        app.logger.warning(f"Skipping invalid quantity: {quantity} for product {sku}")
                        continue
                    
                    # Check for duplicate sales (same product, date and quantity)
                    existing_sale = Sale.query.filter_by(
                        product_id=product.id,
                        sale_date=sale_date,
                        quantity=quantity
                    ).first()
                    
                    if existing_sale:
                        app.logger.info(f"Skipping duplicate sale for product {sku} on {sale_date}")
                        continue
                    
                    # Create sale record
                    sale = Sale(
                        product_id=product.id,
                        quantity=quantity,
                        price=float(price),
                        sale_date=sale_date,
                        user_id=get_jwt_identity()
                    )
                db.session.add(sale)
                sales_created += 1
        
        # Commit all changes
        db.session.commit()
        
        # Trigger model training
        print(f"CSV processing complete. Created {products_created} products and {sales_created} sales. Triggering model training...")
        train_models()
        
        return jsonify({
            "message": "CSV processed successfully",
            "products_created": products_created,
            "sales_created": sales_created
        }), 200
    
    return jsonify({"error": "File must be a CSV"}), 400

# Model training endpoint
@app.route('/api/train', methods=['POST'])
@jwt_required()
def trigger_training():
    print("Manual training triggered")
    train_models()
    return jsonify({"message": "Training triggered successfully"}), 200

# Sales routes
@app.route('/api/sales', methods=['GET'])
@jwt_required()
def get_sales():
    sales = Sale.query.all()
    items = []
    for sale in sales:
        items.append({
            'id': str(sale.id),
            'productId': str(sale.product_id),
            'productName': sale.product.name,
            'quantity': sale.quantity,
            'date': sale.sale_date.isoformat()
        })
    return jsonify({"items": items, "total": len(items)}), 200

@app.route('/api/sales', methods=['POST'])
@jwt_required()
def create_sale():
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity')
    
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    
    if product.stock < quantity:
        return jsonify({"error": "Insufficient stock"}), 400
    
    # Calculate week number and year
    sale_date = datetime.utcnow()
    week_number = sale_date.isocalendar()[1]
    year = sale_date.year
    
    # Create sale record
    new_sale = Sale(
        product_id=product_id,
        quantity=quantity,
        total_price=product.price * quantity,
        sale_date=sale_date,
        week_number=week_number,
        year=year
    )
    
    # Update product stock
    product.stock -= quantity
    
    db.session.add(new_sale)
    db.session.commit()
    
    # Training is handled by weekly scheduler to avoid mid-week retrains
    
    return jsonify({
        'id': new_sale.id,
        'product_id': new_sale.product_id,
        'quantity': new_sale.quantity,
        'total_price': new_sale.total_price,
        'sale_date': new_sale.sale_date.isoformat(),
        'week_number': new_sale.week_number,
        'year': new_sale.year
    }), 201

# Forecast routes
@app.route('/api/forecast', methods=['GET'])
@jwt_required()
def get_forecasts():
    forecasts = Forecast.query.all()
    result = []
    for forecast in forecasts:
        result.append({
            'id': forecast.id,
            'product_id': forecast.product_id,
            'product_name': forecast.product.name,
            'predicted_quantity': forecast.predicted_quantity,
            'week_number': forecast.week_number,
            'year': forecast.year,
            'created_at': forecast.created_at.isoformat()
        })
    return jsonify(result), 200

# Model training function
def train_model():
    logger.info("Starting model training...")
    
    # Get current week and year
    current_date = datetime.utcnow()
    current_week = current_date.isocalendar()[1]
    current_year = current_date.year
    
    # Check if we already trained for this week
    last_training = ModelTraining.query.order_by(ModelTraining.id.desc()).first()
    if last_training and last_training.last_trained_week == current_week and last_training.last_trained_year == current_year:
        logger.info(f"Model already trained for week {current_week}, year {current_year}")
        return
    
    # Get all products
    products = Product.query.all()
    
    for product in products:
        # Get historical sales data for this product
        sales_data = Sale.query.filter_by(product_id=product.id).all()
        
        if len(sales_data) < 4:  # Need at least 4 weeks of data to train
            logger.info(f"Not enough data to train model for product {product.id}")
            continue
        
        # Prepare data for training
        df = pd.DataFrame([{
            'week_number': sale.week_number,
            'year': sale.year,
            'quantity': sale.quantity
        } for sale in sales_data])
        
        # Feature engineering
        df['week_year'] = df['year'] * 100 + df['week_number']
        df = df.sort_values('week_year')
        
        # Create features and target
        X = df[['week_number', 'year']].values
        y = df['quantity'].values
        
        # Train model
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)
        
        # Predict next 4 weeks
        next_weeks = []
        for i in range(1, 5):
            next_week = current_week + i
            next_year = current_year
            if next_week > 52:
                next_week = next_week - 52
                next_year += 1
            next_weeks.append([next_week, next_year])
        
        # Make predictions
        predictions = model.predict(np.array(next_weeks))
        
        # Save predictions to database
        for i, (week, year) in enumerate(next_weeks):
            # Check if forecast already exists
            existing_forecast = Forecast.query.filter_by(
                product_id=product.id,
                week_number=week,
                year=year
            ).first()
            
            if existing_forecast:
                existing_forecast.predicted_quantity = max(0, predictions[i])
            else:
                new_forecast = Forecast(
                    product_id=product.id,
                    predicted_quantity=max(0, predictions[i]),
                    week_number=week,
                    year=year
                )
                db.session.add(new_forecast)
        
    # Record training
    new_training = ModelTraining(
        last_trained_week=current_week,
        last_trained_year=current_year,
        accuracy=0.85  # Placeholder, in production calculate actual accuracy
    )
    db.session.add(new_training)
    db.session.commit()
    
    logger.info(f"Model training completed for week {current_week}, year {current_year}")

def check_and_train_model():
    # Get current week and year
    current_date = datetime.utcnow()
    current_week = current_date.isocalendar()[1]
    current_year = current_date.year
    
    # Check if we already trained for this week
    last_training = ModelTraining.query.order_by(ModelTraining.id.desc()).first()
    
    if not last_training or last_training.last_trained_week != current_week or last_training.last_trained_year != current_year:
        # Start training in a separate thread to not block the request
        threading.Thread(target=train_model).start()

# Weekly training scheduler
def weekly_training_scheduler():
    import datetime as dt
    while True:
        try:
            with app.app_context():
                train_model()
        except Exception as e:
            logger.error(f"Error in weekly training: {str(e)}")

        # Sleep until next Monday 00:05 UTC
        now = dt.datetime.utcnow()
        days_ahead = (7 - now.weekday()) % 7  # 0=Monday
        if days_ahead == 0 and (now.hour < 0 or (now.hour == 0 and now.minute < 5)):
            days_ahead = 0
        elif days_ahead == 0:
            days_ahead = 7
        next_monday = (now + dt.timedelta(days=days_ahead)).replace(hour=0, minute=5, second=0, microsecond=0)
        sleep_seconds = max(60, (next_monday - now).total_seconds())
        time.sleep(sleep_seconds)

# Start the scheduler in a separate thread when the app starts
@app.before_first_request
def start_scheduler():
    threading.Thread(target=weekly_training_scheduler, daemon=True).start()

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8000)))