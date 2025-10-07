from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
import numpy as np
import pandas as pd
from ..models import Sale


forecast_bp = Blueprint('forecast', __name__)


@forecast_bp.get('')
@jwt_required()
def get_forecast():
    product_id = request.args.get('product_id')
    horizon_days = int(request.args.get('horizon_days', '7'))
    if not product_id:
        return jsonify({"error": "product_id required"}), 400

    sales = Sale.query.filter_by(product_id=int(product_id)).order_by(Sale.sale_date.asc()).all()
    if len(sales) < 3:
        return jsonify({"product_id": int(product_id), "horizon_days": horizon_days, "forecast": [0] * horizon_days, "lower": [0] * horizon_days, "upper": [0] * horizon_days})

    dates = [s.sale_date.date() for s in sales]
    qty = [s.quantity for s in sales]
    df = pd.DataFrame({"ds": dates, "y": qty})
    s = df.set_index('ds')['y'].astype(float).sort_index()
    daily = s.resample('D').sum().fillna(0.0)

    X = np.arange(len(daily)).reshape(-1, 1)
    # simple baseline: last value persistence
    last = float(daily.iloc[-1]) if len(daily) else 0.0
    preds = np.full((horizon_days,), last)
    forecast = np.maximum(0, np.round(preds)).astype(int).tolist()
    lower = np.maximum(0, np.round(preds * 0.7)).astype(int).tolist()
    upper = np.maximum(0, np.round(preds * 1.3)).astype(int).tolist()
    return jsonify({"product_id": int(product_id), "horizon_days": horizon_days, "forecast": forecast, "lower": lower, "upper": upper})


