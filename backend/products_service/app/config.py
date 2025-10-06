from __future__ import annotations
from dataclasses import dataclass
from shared.config import load_config, ServiceConfig


@dataclass
class ProductsServiceConfig(ServiceConfig):
    pass


def load_service_config() -> ProductsServiceConfig:
    base = load_config("products-service")
    return ProductsServiceConfig(**base.__dict__)
