from __future__ import annotations
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import BigInteger


class Base(DeclarativeBase):
    pass


class ProcessedSale(Base):
    __tablename__ = "processed_sales"

    sale_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
