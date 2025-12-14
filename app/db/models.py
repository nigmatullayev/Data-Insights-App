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


class SupportTicket(Base):
    __tablename__ = "support_tickets"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    status = Column(String, default="open")  # open, in_progress, resolved, closed
    priority = Column(String, default="medium")  # low, medium, high, urgent
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    external_id = Column(String, nullable=True)  # GitHub Issue ID, Trello ID, etc.
    external_url = Column(String, nullable=True)  # Link to external ticket