import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import datetime as dt
import os
import pickle
import joblib
from .extensions import db
from .models import Product, Sale, Forecast, ModelTraining


def train_weekly_models() -> None:
    now = dt.datetime.utcnow()
    current_week = now.isocalendar()[1]
    current_year = now.year
    last = ModelTraining.query.order_by(ModelTraining.id.desc()).first()
    if last and last.last_trained_week == current_week and last.last_trained_year == current_year:
        return
    _train_and_save(current_week, current_year)


def train_now() -> None:
    now = dt.datetime.utcnow()
    current_week = now.isocalendar()[1]
    current_year = now.year
    _train_and_save(current_week, current_year)


def _train_and_save(current_week: int, current_year: int) -> None:
    try:
        print("Starting model training...")
        
        # Create models directory if it doesn't exist
        models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'models')
        if not os.path.exists(models_dir):
            os.makedirs(models_dir)
            print(f"Created models directory at {models_dir}")
        
        # Create a lock file to indicate training is in progress
        lock_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'training_in_progress.lock')
        with open(lock_file, 'w') as f:
            f.write(f"Training started at {dt.datetime.now()}")
        
        products = Product.query.all()
        
        if not products:
            print("No products found in database")
            os.remove(lock_file)
            return
            
        print(f"Found {len(products)} products to process")
        
        for p in products:
            sales = Sale.query.filter_by(product_id=p.id).all()
            if len(sales) < 4:
                print(f"Skipping product {p.id} - not enough sales data (only {len(sales)} records)")
                continue
                
            print(f"Training model for product {p.id} with {len(sales)} sales records")
            
            # Ensure sales have week_number and year
            for sale in sales:
                if not sale.week_number or not sale.year:
                    # Calculate week_number and year if missing
                    iso = sale.sale_date.isocalendar()
                    sale.week_number = iso[1]
                    sale.year = sale.sale_date.year
            
            # Create a DataFrame with daily sales data
            sales_by_date = {}
            for sale in sales:
                date_str = sale.sale_date.strftime('%Y-%m-%d')
                if date_str in sales_by_date:
                    sales_by_date[date_str] += sale.quantity
                else:
                    sales_by_date[date_str] = sale.quantity
            
            # Convert to DataFrame and sort by date
            daily_df = pd.DataFrame([
                {'date': date, 'qty': qty, 'day_of_week': dt.datetime.strptime(date, '%Y-%m-%d').weekday()}
                for date, qty in sales_by_date.items()
            ])
            
            if daily_df.empty:
                print(f"Empty dataframe for product {p.id}")
                continue
                
            daily_df = daily_df.sort_values('date')
            
            # Add features for the model
            daily_df['day_of_week'] = daily_df['date'].apply(lambda x: dt.datetime.strptime(x, '%Y-%m-%d').weekday())
            daily_df['month'] = daily_df['date'].apply(lambda x: dt.datetime.strptime(x, '%Y-%m-%d').month)
            daily_df['day'] = daily_df['date'].apply(lambda x: dt.datetime.strptime(x, '%Y-%m-%d').day)
            
            # Create features for daily prediction
            X_daily = daily_df[['day_of_week', 'month', 'day']].values
            y_daily = daily_df['qty'].values
            
            print(f"Training daily model with X shape: {X_daily.shape}, y shape: {y_daily.shape}")
            daily_model = RandomForestRegressor(n_estimators=100, random_state=42)
            daily_model.fit(X_daily, y_daily)
            
            # Save the trained model to a file
            model_path = os.path.join(models_dir, f'product_{p.id}_daily_model.joblib')
            joblib.dump(daily_model, model_path)
            print(f"Saved daily model to {model_path}")
            
            # Generate daily predictions for the next 7 days
            today = dt.datetime.now().date()
            next_days = []
            daily_preds = []
            lower_bounds = []
            upper_bounds = []
            
            for i in range(1, 8):  # Next 7 days
                next_date = today + dt.timedelta(days=i)
                next_day_features = np.array([[
                    next_date.weekday(),  # day_of_week
                    next_date.month,      # month
                    next_date.day         # day
                ]])
                
                pred = daily_model.predict(next_day_features)[0]
                pred = max(0.0, float(pred))
                
                next_days.append(next_date.strftime('%Y-%m-%d'))
                daily_preds.append(pred)
                lower_bounds.append(max(0, pred * 0.8))  # 20% lower bound
                upper_bounds.append(pred * 1.2)          # 20% upper bound
            
            print(f"Daily predictions for next 7 days: {daily_preds}")
            
            # Save daily predictions to database
            for date_str, pred, lower, upper in zip(next_days, daily_preds, lower_bounds, upper_bounds):
                forecast_date = dt.datetime.strptime(date_str, '%Y-%m-%d').date()
                
                # Check if forecast already exists for this date
                f = Forecast.query.filter_by(
                    product_id=p.id, 
                    forecast_date=forecast_date
                ).first()
                
                if f:
                    f.predicted_quantity = pred
                    f.lower_bound = lower
                    f.upper_bound = upper
                else:
                    new_forecast = Forecast(
                        product_id=p.id,
                        predicted_quantity=pred,
                        lower_bound=lower,
                        upper_bound=upper,
                        forecast_date=forecast_date,
                        # Keep week_number and year for compatibility
                        week_number=forecast_date.isocalendar()[1],
                        year=forecast_date.year
                    )
                    db.session.add(new_forecast)
            
            print(f"Saved daily forecasts for product {p.id}")
            
            # Also save weekly forecasts for backward compatibility
            weekly_df = pd.DataFrame([{'week': s.week_number, 'year': s.year, 'qty': s.quantity} for s in sales])
            weekly_df = weekly_df.sort_values(['year', 'week'])
            
            if not weekly_df.empty:
                X_weekly = weekly_df[['week', 'year']].values
                y_weekly = weekly_df['qty'].values
                
                weekly_model = RandomForestRegressor(n_estimators=100, random_state=42)
                weekly_model.fit(X_weekly, y_weekly)
                
                next_weeks = []
                w = current_week
                yyear = current_year
                for _ in range(4):
                    w += 1
                    if w > 52:
                        w = 1
                        yyear += 1
                    next_weeks.append([w, yyear])
                
                weekly_preds = weekly_model.predict(np.array(next_weeks))
                
                # Save weekly model
                weekly_model_path = os.path.join(models_dir, f'product_{p.id}_weekly_model.joblib')
                joblib.dump(weekly_model, weekly_model_path)

        mt = ModelTraining(last_trained_week=current_week, last_trained_year=current_year, accuracy=0.0)
        db.session.add(mt)
        db.session.commit()
        
        # Remove the lock file when training is complete
        if os.path.exists(lock_file):
            os.remove(lock_file)
            
        print("Model training completed successfully")
    except Exception as e:
        print(f"Error in model training: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Remove lock file in case of error
        lock_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'training_in_progress.lock')
        if os.path.exists(lock_file):
            os.remove(lock_file)
            
        # Rollback any partial changes
        db.session.rollback()
        raise


