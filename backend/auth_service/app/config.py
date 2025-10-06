from __future__ import annotations
from dataclasses import dataclass
from shared.config import load_config, ServiceConfig


@dataclass
class AuthServiceConfig(ServiceConfig):
    access_token_ttl: int = 15 * 60
    refresh_token_ttl: int = 7 * 24 * 3600


def load_service_config() -> AuthServiceConfig:
    base = load_config("auth-service")
    return AuthServiceConfig(**base.__dict__)
