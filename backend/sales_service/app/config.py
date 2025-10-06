from __future__ import annotations
from dataclasses import dataclass
from shared.config import load_config, ServiceConfig


@dataclass
class SalesServiceConfig(ServiceConfig):
    pass


def load_service_config() -> SalesServiceConfig:
    base = load_config("sales-service")
    return SalesServiceConfig(**base.__dict__)
