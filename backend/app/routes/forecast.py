from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
import numpy as np
import pandas as pd
import datetime as dt
import os
import joblib
from ..extensions import db
from ..models import Sale, ModelTraining, Forecast, Product


forecast_bp = Blueprint('forecast', __name__)


@forecast_bp.route('', methods=['GET'])
@jwt_required()
def get_product_forecast():
    product_id = request.args.get('product_id')
    horizon_days = int(request.args.get('horizon_days', 7))
    
    if not product_id:
        return jsonify({"error": "product_id required"}), 400
    
    # Get product info
    product = Product.query.get(int(product_id))
    if not product:
        return jsonify({"error": "Product not found"}), 404
    
    # Get forecasts for the product
    today = dt.datetime.now().date()
    forecasts = Forecast.query.filter(
        Forecast.product_id == int(product_id),
        Forecast.forecast_date >= today
    ).order_by(Forecast.forecast_date.asc()).limit(horizon_days).all()
    
    # Check if training is in progress - ModelTraining doesn't have product_id
    training_in_progress = ModelTraining.query.filter(
        ModelTraining.trained_at >= today - dt.timedelta(hours=1)
    ).first() is not None
    
    # Format forecast data
    forecast_data = []
    if forecasts:
        for forecast in forecasts:
            forecast_data.append({
                "date": forecast.forecast_date.strftime('%Y-%m-%d'),
                "prediction": forecast.predicted_quantity,
                "lower_bound": forecast.lower_bound,
                "upper_bound": forecast.upper_bound
            })
    else:
        # If no forecasts are available, generate default empty forecasts for the next 7 days
        for i in range(1, horizon_days + 1):
            next_date = today + dt.timedelta(days=i)
            forecast_data.append({
                "date": next_date.strftime('%Y-%m-%d'),
                "prediction": 0,
                "lower_bound": 0,
                "upper_bound": 0
            })
    
    return jsonify({
        "product_id": int(product_id),
        "forecast": forecast_data,
        "training_in_progress": training_in_progress
    })


@forecast_bp.route('/comparison', methods=['GET', 'OPTIONS'])
@jwt_required(optional=True)
def get_forecast_comparison():
    if request.method == 'OPTIONS':
        return '', 200
        
    product_id = request.args.get('product_id')
    if not product_id:
        return jsonify({"error": "product_id required"}), 400
    
    # Get product info
    product = Product.query.get(int(product_id))
    if not product:
        return jsonify({"error": "Product not found"}), 404
    
    # Get actual sales data for the past 4 weeks
    today = dt.datetime.now().date()
    four_weeks_ago = today - dt.timedelta(days=28)
    
    sales = Sale.query.filter(
        Sale.product_id == int(product_id),
        Sale.sale_date >= four_weeks_ago
    ).order_by(Sale.sale_date.asc()).all()
    
    # Group sales by date
    sales_by_date = {}
    for sale in sales:
        date_str = sale.sale_date.strftime('%Y-%m-%d')
        if date_str in sales_by_date:
            sales_by_date[date_str] += sale.quantity
        else:
            sales_by_date[date_str] = sale.quantity
    
    # Get forecasts for the same period
    forecasts = Forecast.query.filter(
        Forecast.product_id == int(product_id),
        Forecast.forecast_date >= four_weeks_ago,
        Forecast.forecast_date <= today
    ).order_by(Forecast.forecast_date.asc()).all()
    
    # Group forecasts by date
    forecasts_by_date = {}
    for forecast in forecasts:
        date_str = forecast.forecast_date.strftime('%Y-%m-%d')
        forecasts_by_date[date_str] = forecast.predicted_quantity
    
    # Combine data for comparison
    comparison_data = []
    current_date = four_weeks_ago
    while current_date <= today:
        date_str = current_date.strftime('%Y-%m-%d')
        actual = sales_by_date.get(date_str, 0)
        predicted = forecasts_by_date.get(date_str, None)
        
        comparison_data.append({
            "date": date_str,
            "actual": actual,
            "predicted": predicted
        })
        
        current_date += dt.timedelta(days=1)
    
    return jsonify({
        "product_id": int(product_id),
        "product_name": product.name,
        "comparison_data": comparison_data
    })


