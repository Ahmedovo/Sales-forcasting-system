from __future__ import annotations
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import BigInteger
from shared.config import load_config


class Base(DeclarativeBase):
    pass


class ProcessedSale(Base):
    __tablename__ = "processed_sales"
    __table_args__ = {"schema": (load_config("forecast-service").db_schema or "forecast")}

    sale_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
