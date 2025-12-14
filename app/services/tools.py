from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db import models
from app.core.safety import validate_table_name

def get_row_count(db: Session, table: str):
    """
    Get row count for a table with safety validation
    """
    if not validate_table_name(table):
        raise ValueError(f"Invalid table name: {table}")
    
    if table == "users":
        return db.query(func.count(models.User.id)).scalar() or 0
    if table == "orders":
        return db.query(func.count(models.Order.id)).scalar() or 0
    if table == "sales":
        return db.query(func.count(models.Sale.id)).scalar() or 0
    return 0


def get_recent_records(db: Session, table: str, limit: int = 10):
    if table == "orders":
        orders = db.query(models.Order).order_by(models.Order.created_at.desc()).limit(limit).all()
        return [
            {
                "id": order.id,
                "user_id": order.user_id,
                "product": order.product,
                "amount": order.amount,
                "created_at": order.created_at.isoformat() if order.created_at else None
            }
            for order in orders
        ]
    if table == "sales":
        sales = db.query(models.Sale).order_by(models.Sale.created_at.desc()).limit(limit).all()
        return [
            {
                "id": sale.id,
                "order_id": sale.order_id,
                "revenue": sale.revenue,
                "created_at": sale.created_at.isoformat() if sale.created_at else None
            }
            for sale in sales
        ]
    return []


def get_sales_stats(db: Session):
    return {
        "total_sales": db.query(func.sum(models.Sale.revenue)).scalar(),
        "avg_sales": db.query(func.avg(models.Sale.revenue)).scalar(),
        "max_sale": db.query(func.max(models.Sale.revenue)).scalar()
    }
