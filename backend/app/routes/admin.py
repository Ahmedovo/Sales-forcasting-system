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

    # Simple ETL: accept CSV with headers: name,price,stock OR productId,quantity,date
    content = file.read().decode('utf-8')
    reader = csv.DictReader(io.StringIO(content))
    inserted_products = 0
    inserted_sales = 0

    for row in reader:
        # Normalize keys (strip spaces, lowercase)
        normalized = { (k or '').strip().lower(): (v or '').strip() for k, v in row.items() }
        if {'name','price'}.issubset(normalized.keys()):
            name = normalized.get('name')
            price = float(normalized.get('price') or 0)
            stock = int(normalized.get('stock') or 0)
            p = Product(name=name, price=price, stock=stock)
            db.session.add(p)
            inserted_products += 1
        elif {'productid','quantity','date'}.issubset(normalized.keys()):
            product_id = int(normalized.get('productid'))
            quantity = int(normalized.get('quantity'))
            date_str = normalized.get('date')
            sale_date = dt.datetime.fromisoformat(date_str)
            product = Product.query.get(product_id)
            if not product:
                continue
            if product.stock < quantity:
                # allow negative stock in import? For now skip
                continue
            iso = sale_date.isocalendar()
            sale = Sale(product_id=product_id, quantity=quantity, total_price=product.price * quantity, sale_date=sale_date, week_number=iso[1], year=sale_date.year)
            product.stock -= quantity
            db.session.add(sale)
            inserted_sales += 1
        else:
            # skip unknown row type
            continue

    db.session.commit()
    return jsonify({"inserted_products": inserted_products, "inserted_sales": inserted_sales})


@admin_bp.post('/train-now')
@jwt_required()
def admin_train_now():
    user = User.query.get(get_jwt_identity())
    if not _is_admin(user):
        return jsonify({"error": "forbidden"}), 403
    train_now()
    return jsonify({"status": "training triggered"})


