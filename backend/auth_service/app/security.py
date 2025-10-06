from __future__ import annotations
import bcrypt
from shared.jwt_utils import JWTManager
from .config import load_service_config


def get_jwt_manager() -> JWTManager:
    cfg = load_service_config()
    return JWTManager(
        algorithm=cfg.jwt_algorithm,
        secret=cfg.jwt_secret,
        private_key_path=cfg.jwt_private_key_path,
        public_key_path=cfg.jwt_public_key_path,
    )


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except Exception:
        return False
