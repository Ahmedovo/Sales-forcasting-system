from __future__ import annotations
from flask import Blueprint, request, jsonify
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from threading import RLock

forecast_bp = Blueprint("forecast", __name__)

# In-memory time series store: product_id -> pandas Series (datetime index, quantity)
_series_store: dict[int, pd.Series] = {}
_store_lock = RLock()


def update_series(product_id: int, sold_at_iso: str, quantity: int) -> None:
    import datetime as dt
    ts = dt.datetime.fromisoformat(sold_at_iso)
    with _store_lock:
        s = _series_store.get(product_id)
        if s is None:
            _series_store[product_id] = pd.Series([quantity], index=[ts])
        else:
            s.loc[ts] = s.get(ts, 0) + quantity
            _series_store[product_id] = s.sort_index()


@forecast_bp.get("/forecast")
def get_forecast():
    try:
        product_id = int(request.args.get("product_id"))
    except Exception:
        return jsonify({"error": "product_id required"}), 400
    horizon_days = int(request.args.get("horizon_days", 7))

    with _store_lock:
        series = _series_store.get(product_id)
    if series is None or len(series) < 3:
        # Not enough data, return zeros
        return jsonify({"product_id": product_id, "horizon_days": horizon_days, "forecast": [0] * horizon_days, "lower": [0] * horizon_days, "upper": [0] * horizon_days})

    # Resample to daily sum
    daily = series.resample('D').sum()

    try:
        model = ARIMA(daily, order=(1, 1, 1))
        fit = model.fit()
        pred = fit.get_forecast(steps=horizon_days)
        forecast = pred.predicted_mean.clip(lower=0).round().astype(int).tolist()
        conf_int = pred.conf_int(alpha=0.2)
        lower = conf_int.iloc[:, 0].clip(lower=0).round().astype(int).tolist()
        upper = conf_int.iloc[:, 1].clip(lower=0).round().astype(int).tolist()
    except Exception:
        # Fallback naive forecast
        last = int(daily.iloc[-1]) if len(daily) else 0
        forecast = [last] * horizon_days
        lower = [max(0, last // 2)] * horizon_days
        upper = [last * 2] * horizon_days

    return jsonify({"product_id": product_id, "horizon_days": horizon_days, "forecast": forecast, "lower": lower, "upper": upper})
