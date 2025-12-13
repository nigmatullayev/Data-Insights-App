from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db import models

def get_row_count(db: Session, table: str):
    if table == "users":
        return db.query(func.count(models.User.id)).scalar()
    if table == "orders":
        return db.query(func.count(models.Order.id)).scalar()
    if table == "sales":
        return db.query(func.count(models.Sale.id)).scalar()
    return None


def get_recent_records(db: Session, table: str, limit: int = 10):
    if table == "orders":
        return db.query(models.Order).order_by(models.Order.created_at.desc()).limit(limit).all()
    if table == "sales":
        return db.query(models.Sale).order_by(models.Sale.created_at.desc()).limit(limit).all()
    return []


def get_sales_stats(db: Session):
    return {
        "total_sales": db.query(func.sum(models.Sale.revenue)).scalar(),
        "avg_sales": db.query(func.avg(models.Sale.revenue)).scalar(),
        "max_sale": db.query(func.max(models.Sale.revenue)).scalar()
    }
