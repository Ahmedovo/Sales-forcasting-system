from __future__ import annotations
from sqlalchemy.orm import sessionmaker
from shared.db import create_engine_with_schema, create_session_factory
from shared.config import load_config
from models import Base


def get_session_factory() -> sessionmaker:
    cfg = load_config("forecast-service")
    engine = create_engine_with_schema(cfg.db_url, cfg.db_schema or "forecast")
    Base.metadata.create_all(engine)
    return create_session_factory(engine)
