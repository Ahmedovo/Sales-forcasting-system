from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from ..extensions import db
from ..models import Product


products_bp = Blueprint('products', __name__)


@products_bp.get('')
@jwt_required()
def list_products():
    products = Product.query.order_by(Product.id.asc()).all()
    items = [{'id': str(p.id), 'name': p.name, 'price': p.price, 'stock': p.stock} for p in products]
    return jsonify({"items": items, "total": len(items)})


@products_bp.post('')
@jwt_required()
def create_product():
    data = request.get_json() or {}
    name = data.get('name')
    price = data.get('price')
    stock = int(data.get('stock', 0))
    if not name or price is None:
        return jsonify({"error": "name and price required"}), 400
    p = Product(name=name, price=float(price), stock=stock)
    db.session.add(p)
    db.session.commit()
    return jsonify({'id': str(p.id), 'name': p.name, 'price': p.price, 'stock': p.stock}), 201


@products_bp.put('/<int:product_id>')
@jwt_required()
def update_product(product_id: int):
    p = Product.query.get_or_404(product_id)
    data = request.get_json() or {}
    if 'name' in data:
        p.name = data['name']
    if 'price' in data:
        p.price = float(data['price'])
    if 'stock' in data:
        p.stock = int(data['stock'])
    db.session.commit()
    return jsonify({'id': str(p.id), 'name': p.name, 'price': p.price, 'stock': p.stock})


@products_bp.delete('/<int:product_id>')
@jwt_required()
def delete_product(product_id: int):
    p = Product.query.get_or_404(product_id)
    db.session.delete(p)
    db.session.commit()
    return jsonify({"message": "deleted"})


