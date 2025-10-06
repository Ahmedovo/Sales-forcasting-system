from __future__ import annotations
from dataclasses import dataclass
from shared.config import load_config, ServiceConfig


@dataclass
class ForecastServiceConfig(ServiceConfig):
    retrain_threshold: int = 50


def load_service_config() -> ForecastServiceConfig:
    base = load_config("forecast-service")
    return ForecastServiceConfig(**base.__dict__)
