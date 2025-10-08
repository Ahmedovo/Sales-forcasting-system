from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
import io
import csv
import datetime as dt
from ..extensions import db
from ..models import User, Product, Sale
from ..training import train_now


admin_bp = Blueprint('admin', __name__)


def _is_admin(user: User) -> bool:
    # Simple: treat username 'admin' as admin; extend with roles later
    return user and user.username == 'admin'


@admin_bp.post('/upload-csv')
@jwt_required()
def upload_csv():
    user = User.query.get(get_jwt_identity())
    if not _is_admin(user):
        return jsonify({"error": "forbidden"}), 403

    if 'file' not in request.files:
        return jsonify({"error": "file missing"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "empty filename"}), 400

# Simple ETL: accept CSV with headers:
# - product rows: name,sku,price,stock
# - sales rows: product (name), sku, product price, stock, quantity sale, date of sale
    content = file.read().decode('utf-8')
    reader = csv.DictReader(io.StringIO(content))
    inserted_products = 0
    inserted_sales = 0

    for row in reader:
        # Normalize keys (strip spaces, lowercase)
        normalized = { (k or '').strip().lower(): (v or '').strip() for k, v in row.items() }

        # Product upsert row
        if {'name','sku','price'}.issubset(normalized.keys()):
            name = normalized.get('name')
            sku = normalized.get('sku')
            price = float(normalized.get('price') or 0)
            stock = int(normalized.get('stock') or 0)
            if not sku:
                continue
            existing = Product.query.filter_by(sku=sku).first()
            if existing:
                existing.name = name or existing.name
                existing.price = price if price else existing.price
                if 'stock' in normalized:
                    existing.stock = stock
            else:
                db.session.add(Product(name=name, sku=sku, price=price, stock=stock))
                inserted_products += 1

        # Sales row from the specified schema
        elif {'product name','sku','product price','stock','quantity sale','date of sale'}.issubset(normalized.keys()):
            name = normalized.get('product name')
            sku = normalized.get('sku')
            price = float(normalized.get('product price') or 0)
            stock = int(normalized.get('stock') or 0)
            qty = int(normalized.get('quantity sale') or 0)
            date_str = normalized.get('date of sale')
            try:
                sale_date = dt.datetime.fromisoformat(date_str)
            except Exception:
                # try common alternative formats
                try:
                    sale_date = dt.datetime.strptime(date_str, '%Y-%m-%d')
                except Exception:
                    continue

            if not sku:
                continue
            product = Product.query.filter_by(sku=sku).first()
            if not product:
                product = Product(name=name or sku, sku=sku, price=price, stock=stock)
                db.session.add(product)
                db.session.flush()
                inserted_products += 1

            if product.stock < qty:
                # allow oversell? For now, cap to available stock
                qty = max(0, product.stock)
            if qty <= 0:
                continue

            iso = sale_date.isocalendar()
            sale = Sale(product_id=product.id, quantity=qty, total_price=product.price * qty, sale_date=sale_date, week_number=iso[1], year=sale_date.year)
            product.stock -= qty
            db.session.add(sale)
            inserted_sales += 1
        else:
            # skip unknown row type
            continue

    db.session.commit()
    # Trigger retrain after import completes
    try:
        train_now()
    except Exception:
        pass
    return jsonify({"inserted_products": inserted_products, "inserted_sales": inserted_sales})


@admin_bp.post('/train-now')
@jwt_required()
def admin_train_now():
    user = User.query.get(get_jwt_identity())
    if not _is_admin(user):
        return jsonify({"error": "forbidden"}), 403
    train_now()
    return jsonify({"status": "training triggered"})


