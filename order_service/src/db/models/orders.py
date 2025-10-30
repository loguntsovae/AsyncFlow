from sqlalchemy import Column, Integer, Float, DateTime, func, String
from src.db.base import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String(length=32), nullable=False, server_default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
