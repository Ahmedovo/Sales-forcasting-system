from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError, OperationalError
from ..extensions import db
from ..models import Product


products_bp = Blueprint('products', __name__)


@products_bp.get('')
@jwt_required()
def list_products():
    products = Product.query.order_by(Product.id.asc()).all()
    items = [{'id': str(p.id), 'name': p.name, 'sku': p.sku, 'price': p.price, 'stock': p.stock} for p in products]
    return jsonify({"items": items, "total": len(items)})


@products_bp.post('')
@jwt_required()
def create_product():
    data = request.get_json() or {}
    sku = data.get('sku')
    name = data.get('name')
    price = data.get('price')
    stock = int(data.get('stock', 0))
    if not sku or not name or price is None:
        return jsonify({"error": "sku, name and price required"}), 400
    # upsert by sku if exists
    try:
        existing = Product.query.filter_by(sku=sku).first()
    except OperationalError as e:
        # Likely missing 'sku' column in database schema
        return jsonify({"error": "Database schema out of date. Please add 'sku' column to products table and make it unique."}), 500
    if existing:
        existing.name = name
        existing.price = float(price)
        existing.stock = stock if stock is not None else existing.stock
        db.session.commit()
        return jsonify({'id': str(existing.id), 'name': existing.name, 'sku': existing.sku, 'price': existing.price, 'stock': existing.stock}), 200

    p = Product(sku=sku, name=name, price=float(price), stock=stock)
    db.session.add(p)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "SKU must be unique"}), 409
    return jsonify({'id': str(p.id), 'name': p.name, 'sku': p.sku, 'price': p.price, 'stock': p.stock}), 201


@products_bp.put('/<int:product_id>')
@jwt_required()
def update_product(product_id: int):
    p = Product.query.get_or_404(product_id)
    data = request.get_json() or {}
    if 'sku' in data:
        p.sku = data['sku']
    if 'name' in data:
        p.name = data['name']
    if 'price' in data:
        p.price = float(data['price'])
    if 'stock' in data:
        p.stock = int(data['stock'])
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "SKU must be unique"}), 409
    return jsonify({'id': str(p.id), 'name': p.name, 'sku': p.sku, 'price': p.price, 'stock': p.stock})


@products_bp.delete('/<int:product_id>')
@jwt_required()
def delete_product(product_id: int):
    p = Product.query.get_or_404(product_id)
    db.session.delete(p)
    db.session.commit()
    return jsonify({"message": "deleted"})


@products_bp.get('/alerts')
@jwt_required()
def low_stock_alerts():
    try:
        threshold = int(request.args.get('threshold', '10'))
    except Exception:
        threshold = 10
    products = Product.query.filter(Product.stock <= threshold).order_by(Product.stock.asc()).all()
    alerts = [{'id': str(p.id), 'name': p.name, 'sku': p.sku, 'stock': p.stock} for p in products]
    return jsonify({"items": alerts, "total": len(alerts), "threshold": threshold})


