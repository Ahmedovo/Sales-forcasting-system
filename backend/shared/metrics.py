from __future__ import annotations
from flask import Blueprint, Response
from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, generate_latest, multiprocess


def create_metrics_blueprint() -> Blueprint:
    bp = Blueprint("metrics", __name__)

    @bp.route("/metrics")
    def metrics() -> Response:
        registry = CollectorRegistry()
        multiprocess.MultiProcessCollector(registry)
        data = generate_latest(registry)
        return Response(data, mimetype=CONTENT_TYPE_LATEST)

    @bp.route("/health")
    def health() -> dict:
        return {"status": "ok"}

    return bp
