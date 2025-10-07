from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
import datetime as dt
from ..extensions import db
from ..models import Product, Sale


sales_bp = Blueprint('sales', __name__)


@sales_bp.get('')
@jwt_required()
def list_sales():
    sales = Sale.query.order_by(Sale.id.desc()).all()
    items = [{
        'id': str(s.id),
        'productId': str(s.product_id),
        'productName': s.product.name,
        'quantity': s.quantity,
        'date': s.sale_date.date().isoformat(),
    } for s in sales]
    return jsonify({"items": items, "total": len(items)})


@sales_bp.post('')
@jwt_required()
def create_sale():
    data = request.get_json() or {}
    try:
        product_id = int(data.get('productId'))
        quantity = int(data.get('quantity'))
        sale_date_str = data.get('date')
        sale_date = dt.datetime.fromisoformat(sale_date_str)
    except Exception:
        return jsonify({"error": "productId, quantity, date required"}), 400

    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    if product.stock < quantity:
        return jsonify({"error": "Insufficient stock"}), 400

    iso = sale_date.isocalendar()
    week_number = iso[1]
    year = sale_date.year

    sale = Sale(
        product_id=product_id,
        quantity=quantity,
        total_price=product.price * quantity,
        sale_date=sale_date,
        week_number=week_number,
        year=year,
    )
    product.stock -= quantity
    db.session.add(sale)
    db.session.commit()
    return jsonify({
        'id': str(sale.id),
        'productId': str(sale.product_id),
        'productName': sale.product.name,
        'quantity': sale.quantity,
        'date': sale.sale_date.date().isoformat(),
    }), 201


