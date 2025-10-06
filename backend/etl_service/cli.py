from __future__ import annotations
from flask import Flask, jsonify, request
from shared.kafka import create_json_producer, KafkaConfig
from shared.config import load_config
import random
import datetime as dt

app = Flask(__name__)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/etl/synthetic_sales")
def synthetic_sales():
    cfg = load_config("etl-service")
    producer = create_json_producer(KafkaConfig(bootstrap_servers=cfg.kafka_bootstrap_servers, client_id="etl-service"))
    size = int(request.args.get("size", 100))
    product_id = int(request.args.get("product_id", 1))
    now = dt.datetime.utcnow()
    for i in range(size):
        sold_at = (now - dt.timedelta(days=random.randint(0, 60))).isoformat()
        qty = random.randint(1, 5)
        price = round(random.uniform(5, 50), 2)
        producer.send("sales.created", key=str(100000 + i), value={
            "sale_id": 100000 + i,
            "product_id": product_id,
            "quantity": qty,
            "price": price,
            "sold_at": sold_at,
            "user_id": 1,
        })
    producer.flush(2)
    return jsonify({"emitted": size})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8010)
