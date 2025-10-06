from __future__ import annotations
from flask import Blueprint, request, jsonify
from sqlalchemy import select, text
from decimal import Decimal
from .db import get_session_factory
from models import Base, Sale
from shared.db import create_engine_with_schema
from shared.config import load_config
from shared.kafka import create_json_producer, KafkaConfig
from .auth import require_jwt

sales_bp = Blueprint("sales", __name__)

_cfg = load_config("sales-service")
_engine = create_engine_with_schema(_cfg.db_url, _cfg.db_schema or "sales")
Base.metadata.create_all(_engine)
SessionLocal = get_session_factory()
producer = create_json_producer(KafkaConfig(bootstrap_servers=_cfg.kafka_bootstrap_servers, client_id="sales-service"))


@sales_bp.post("")
@require_jwt
def create_sale():
    data = request.get_json(force=True) or {}
    product_id = data.get("product_id")
    quantity = int(data.get("quantity", 0))
    price = data.get("price")
    sold_at = data.get("sold_at")
    if not all([product_id, quantity > 0, sold_at]):
        return jsonify({"error": "product_id, quantity>0, sold_at required"}), 400

    # transaction: check product stock and decrement in products schema using SQL
    with SessionLocal().bind.begin() as conn:
        # lock product row
        prod = conn.execute(text("""
            SELECT id, stock, price FROM products.products
            WHERE id = :pid
            FOR UPDATE
        """), {"pid": product_id}).mappings().first()
        if not prod:
            return jsonify({"error": "product not found"}), 404
        unit_price = Decimal(str(price if price is not None else prod["price"]))
        if prod["stock"] < quantity:
            return jsonify({"error": "insufficient stock"}), 400
        new_stock = prod["stock"] - quantity
        conn.execute(text("""
            UPDATE products.products SET stock = :new_stock WHERE id = :pid
        """), {"new_stock": new_stock, "pid": product_id})

    # create sale record
    sale = Sale(product_id=product_id, user_id=(int(request.user.get("sub")) if hasattr(request, "user") else None), quantity=quantity, price=unit_price, sold_at=__import__("datetime").datetime.fromisoformat(sold_at))
    with SessionLocal() as session:
        session.add(sale)
        session.commit()
        producer.send("sales.created", key=str(sale.id), value={
            "sale_id": sale.id,
            "product_id": sale.product_id,
            "quantity": sale.quantity,
            "price": float(sale.price),
            "sold_at": sale.sold_at.isoformat(),
            "user_id": sale.user_id,
        })
        producer.flush(1)
        return jsonify({
            "id": sale.id,
            "product_id": sale.product_id,
            "quantity": sale.quantity,
            "price": float(sale.price),
            "sold_at": sale.sold_at.isoformat(),
            "user_id": sale.user_id,
        }), 201


@sales_bp.get("")
@require_jwt
def list_sales():
    product_id = request.args.get("product_id")
    from_dt = request.args.get("from")
    to_dt = request.args.get("to")
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 50))

    query = select(Sale)
    if product_id:
        query = query.where(Sale.product_id == int(product_id))
    if from_dt:
        query = query.where(Sale.sold_at >= __import__("datetime").datetime.fromisoformat(from_dt))
    if to_dt:
        query = query.where(Sale.sold_at <= __import__("datetime").datetime.fromisoformat(to_dt))
    offset = (page - 1) * limit

    with SessionLocal() as session:
        rows = session.scalars(query.offset(offset).limit(limit)).all()
        return jsonify([
            {
                "id": r.id,
                "product_id": r.product_id,
                "user_id": r.user_id,
                "quantity": r.quantity,
                "price": float(r.price),
                "sold_at": r.sold_at.isoformat(),
                "created_at": r.created_at.isoformat(),
            }
            for r in rows
        ])
