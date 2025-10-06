from __future__ import annotations
from functools import wraps
from flask import request, jsonify
from shared.jwt_utils import JWTManager
from .config import load_service_config


_jwt: JWTManager | None = None

def get_jwt() -> JWTManager:
    global _jwt
    if _jwt is None:
        cfg = load_service_config()
        _jwt = JWTManager(
            algorithm=cfg.jwt_algorithm,
            secret=cfg.jwt_secret,
            private_key_path=cfg.jwt_private_key_path,
            public_key_path=cfg.jwt_public_key_path,
        )
    return _jwt


def require_jwt(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.lower().startswith("bearer "):
            return jsonify({"error": "missing bearer token"}), 401
        token = auth.split(" ", 1)[1]
        try:
            payload = get_jwt().decode(token)
            request.user = payload
        except Exception:
            return jsonify({"error": "invalid token"}), 401
        return fn(*args, **kwargs)
    return wrapper
