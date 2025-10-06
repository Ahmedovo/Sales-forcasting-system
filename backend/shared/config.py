import os
from dataclasses import dataclass


@dataclass
class ServiceConfig:
    service_name: str
    debug: bool
    host: str
    port: int
    db_url: str
    db_schema: str | None
    jwt_algorithm: str
    jwt_secret: str | None
    jwt_private_key_path: str | None
    jwt_public_key_path: str | None
    kafka_bootstrap_servers: str


def load_config(service_name: str) -> ServiceConfig:
    return ServiceConfig(
        service_name=service_name,
        debug=os.getenv("DEBUG", "false").lower() == "true",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        db_url=os.getenv("DB_URL", "postgresql+psycopg2://postgres:postgres@postgres:5432/postgres"),
        db_schema=os.getenv("DB_SCHEMA", None),
        jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
        jwt_secret=os.getenv("JWT_SECRET"),
        jwt_private_key_path=os.getenv("JWT_PRIVATE_KEY_PATH"),
        jwt_public_key_path=os.getenv("JWT_PUBLIC_KEY_PATH"),
        kafka_bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
    )
