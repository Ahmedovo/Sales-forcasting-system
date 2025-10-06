from __future__ import annotations
from flask import Blueprint, request, jsonify
from sqlalchemy import select
from decimal import Decimal
from .db import get_session_factory
from ..models import Base, Product
from shared.db import create_engine_with_schema
from shared.config import load_config
from shared.kafka import create_json_producer, KafkaConfig
from .auth import require_jwt

products_bp = Blueprint("products", __name__)

_cfg = load_config("products-service")
_engine = create_engine_with_schema(_cfg.db_url, _cfg.db_schema or "products")
Base.metadata.create_all(_engine)
SessionLocal = get_session_factory()
producer = create_json_producer(KafkaConfig(bootstrap_servers=_cfg.kafka_bootstrap_servers, client_id="products-service"))


def product_to_dict(p: Product) -> dict:
    return {"id": p.id, "name": p.name, "sku": p.sku, "price": float(p.price), "stock": p.stock}


@products_bp.get("")
@require_jwt
def list_products():
    with SessionLocal() as session:
        rows = session.scalars(select(Product)).all()
        return jsonify([product_to_dict(r) for r in rows])


@products_bp.post("")
@require_jwt
def create_product():
    data = request.get_json(force=True) or {}
    name = data.get("name")
    sku = data.get("sku")
    price = data.get("price")
    stock = int(data.get("stock", 0))
    if not all([name, sku, price is not None]):
        return jsonify({"error": "name, sku, price required"}), 400

    prod = Product(name=name, sku=sku, price=Decimal(str(price)), stock=stock)
    with SessionLocal() as session:
        session.add(prod)
        session.commit()
        payload = {"product_id": prod.id, "sku": prod.sku, "name": prod.name, "price": float(prod.price), "stock": prod.stock, "ts": __import__("time").time()}
        producer.send("product.created", key=str(prod.id), value=payload)
        producer.flush(1)
        return jsonify(product_to_dict(prod)), 201


@products_bp.get("/<int:pid>")
@require_jwt
def get_product(pid: int):
    with SessionLocal() as session:
        prod = session.get(Product, pid)
        if not prod:
            return jsonify({"error": "not found"}), 404
        return jsonify(product_to_dict(prod))


@products_bp.put("/<int:pid>")
@require_jwt
def update_product(pid: int):
    data = request.get_json(force=True) or {}
    with SessionLocal() as session:
        prod = session.get(Product, pid)
        if not prod:
            return jsonify({"error": "not found"}), 404
        for field in ["name", "sku", "stock"]:
            if field in data:
                setattr(prod, field, data[field])
        if "price" in data and data["price"] is not None:
            from decimal import Decimal
            prod.price = Decimal(str(data["price"]))
        session.add(prod)
        session.commit()
        producer.send("product.updated", key=str(prod.id), value=product_to_dict(prod))
        producer.flush(1)
        return jsonify(product_to_dict(prod))


@products_bp.delete("/<int:pid>")
@require_jwt
def delete_product(pid: int):
    with SessionLocal() as session:
        prod = session.get(Product, pid)
        if not prod:
            return jsonify({"error": "not found"}), 404
        session.delete(prod)
        session.commit()
        producer.send("product.deleted", key=str(pid), value={"product_id": pid})
        producer.flush(1)
        return jsonify({"status": "deleted"})
