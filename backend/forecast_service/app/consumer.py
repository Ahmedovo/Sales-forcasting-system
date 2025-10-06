from __future__ import annotations
import threading
from shared.kafka import create_json_consumer, KafkaConfig, consume_loop
from shared.config import load_config
from .routes import update_series
from ..models import ProcessedSale
from .db import get_session_factory
from sqlalchemy import select

_consumer_thread: threading.Thread | None = None


def _handler(key: str | None, value: dict) -> None:
    sale_id = int(value.get("sale_id"))
    product_id = int(value.get("product_id"))
    quantity = int(value.get("quantity", 0))
    sold_at = value.get("sold_at")

    SessionLocal = get_session_factory()
    with SessionLocal() as session:
        exists = session.get(ProcessedSale, sale_id)
        if exists:
            return
        update_series(product_id, sold_at, quantity)
        session.add(ProcessedSale(sale_id=sale_id))
        session.commit()


def start_consumer_thread() -> None:
    global _consumer_thread
    if _consumer_thread and _consumer_thread.is_alive():
        return

    cfg = load_config("forecast-service")
    consumer = create_json_consumer(KafkaConfig(bootstrap_servers=cfg.kafka_bootstrap_servers, client_id="forecast-service", group_id="forecast-group"), topics=["sales.created"])

    def run():
        consume_loop(consumer, _handler)

    _consumer_thread = threading.Thread(target=run, daemon=True)
    _consumer_thread.start()
