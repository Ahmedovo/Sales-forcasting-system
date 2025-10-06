from __future__ import annotations
from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from .db import get_session_factory
from .security import get_jwt_manager, hash_password, verify_password
from .config import load_service_config
from models import Base, User
from shared.db import create_engine_with_schema
from shared.config import load_config


auth_bp = Blueprint("auth", __name__)


# Ensure tables exist (simple auto-create; for production use Alembic)
_cfg = load_config("auth-service")
_engine = create_engine_with_schema(_cfg.db_url, _cfg.db_schema or "auth")
Base.metadata.create_all(_engine)
SessionLocal = get_session_factory()


@auth_bp.post("/register")
def register():
    data = request.get_json(force=True) or {}
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "user")

    if not all([name, email, password]):
        return jsonify({"error": "name, email, password required"}), 400

    user = User(name=name, email=email, password_hash=hash_password(password), role=role)
    try:
        with SessionLocal() as session:
            session.add(user)
            session.commit()
            return jsonify({"id": user.id, "name": user.name, "email": user.email, "role": user.role}), 201
    except IntegrityError:
        return jsonify({"error": "email already exists"}), 409


@auth_bp.post("/login")
def login():
    data = request.get_json(force=True) or {}
    email = data.get("email")
    password = data.get("password")
    if not all([email, password]):
        return jsonify({"error": "email and password required"}), 400

    with SessionLocal() as session:
        user = session.scalar(select(User).where(User.email == email))
        if not user or not verify_password(password, user.password_hash):
            return jsonify({"error": "invalid credentials"}), 401

    cfg = load_service_config()
    jwtm = get_jwt_manager()
    access_token = jwtm.encode({"sub": str(user.id), "role": user.role}, cfg.access_token_ttl)
    refresh_token = jwtm.encode({"sub": str(user.id), "type": "refresh"}, cfg.refresh_token_ttl)
    return jsonify({"access_token": access_token, "refresh_token": refresh_token})


@auth_bp.post("/refresh")
def refresh():
    data = request.get_json(force=True) or {}
    refresh_token = data.get("refresh_token")
    if not refresh_token:
        return jsonify({"error": "refresh_token required"}), 400

    jwtm = get_jwt_manager()
    payload = jwtm.decode(refresh_token)
    if payload.get("type") != "refresh":
        return jsonify({"error": "invalid token type"}), 400

    cfg = load_service_config()
    new_access = jwtm.encode({"sub": payload["sub"]}, cfg.access_token_ttl)
    return jsonify({"access_token": new_access})


def _get_bearer_token() -> str | None:
    auth = request.headers.get("Authorization", "")
    if auth.lower().startswith("bearer "):
        return auth.split(" ", 1)[1]
    return None


@auth_bp.get("/me")
def me():
    token = _get_bearer_token()
    if not token:
        return jsonify({"error": "missing bearer token"}), 401
    jwtm = get_jwt_manager()
    payload = jwtm.decode(token)
    user_id = int(payload["sub"]) if isinstance(payload.get("sub"), str) else payload.get("sub")

    with SessionLocal() as session:
        user = session.get(User, user_id)
        if not user:
            return jsonify({"error": "user not found"}), 404
        return jsonify({"id": user.id, "name": user.name, "email": user.email, "role": user.role})
