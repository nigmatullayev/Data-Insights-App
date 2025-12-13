from sqlalchemy import Column,Integer,String,Float,DateTime,ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product = Column(String)
    amount = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")


class Sale(Base):
    __tablename__ = "sales"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    revenue = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order")