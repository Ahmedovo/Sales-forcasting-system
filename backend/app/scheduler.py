import threading
import time
import datetime as dt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from flask import current_app
from .extensions import db
from .models import Product, Sale, Forecast, ModelTraining
from .training import train_weekly_models


def train_weekly_models() -> None:
    now = dt.datetime.utcnow()
    current_week = now.isocalendar()[1]
    current_year = now.year
    last = ModelTraining.query.order_by(ModelTraining.id.desc()).first()
    if last and last.last_trained_week == current_week and last.last_trained_year == current_year:
        return

    products = Product.query.all()
    for p in products:
        sales = Sale.query.filter_by(product_id=p.id).all()
        if len(sales) < 4:
            continue
        rows = [{'week': s.week_number, 'year': s.year, 'qty': s.quantity} for s in sales]
        df = pd.DataFrame(rows).sort_values(['year', 'week'])
        X = df[['week', 'year']].values
        y = df['qty'].values
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)

        next_weeks = []
        w = current_week
        yyear = current_year
        for _ in range(4):
            w += 1
            if w > 52:
                w = 1
                yyear += 1
            next_weeks.append([w, yyear])
        preds = model.predict(np.array(next_weeks))

        for (wk, yr), pred in zip(next_weeks, preds):
            f = Forecast.query.filter_by(product_id=p.id, week_number=wk, year=yr).first()
            if f:
                f.predicted_quantity = max(0.0, float(pred))
            else:
                db.session.add(Forecast(product_id=p.id, predicted_quantity=max(0.0, float(pred)), week_number=wk, year=yr))

    mt = ModelTraining(last_trained_week=current_week, last_trained_year=current_year, accuracy=0.0)
    db.session.add(mt)
    db.session.commit()


def _scheduler_loop():
    while True:
        try:
            with current_app.app_context():
                train_weekly_models()
        except Exception:
            pass
        now = dt.datetime.utcnow()
        days_ahead = (7 - now.weekday()) % 7
        if days_ahead == 0:
            days_ahead = 7
        next_monday = (now + dt.timedelta(days=days_ahead)).replace(hour=0, minute=5, second=0, microsecond=0)
        sleep_seconds = max(60, (next_monday - now).total_seconds())
        time.sleep(sleep_seconds)


def start_scheduler():
    threading.Thread(target=_scheduler_loop, daemon=True).start()


