from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from app.db import models
from app.core.safety import validate_table_name
from datetime import datetime, timedelta
from typing import Optional

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
    total = db.query(func.sum(models.Sale.revenue)).scalar() or 0
    avg = db.query(func.avg(models.Sale.revenue)).scalar() or 0
    max_sale = db.query(func.max(models.Sale.revenue)).scalar() or 0
    min_sale = db.query(func.min(models.Sale.revenue)).scalar() or 0
    
    return {
        "total_sales": float(total),
        "avg_sales": float(avg),
        "max_sale": float(max_sale),
        "min_sale": float(min_sale),
        "total_count": db.query(func.count(models.Sale.id)).scalar() or 0
    }


def get_user_stats(db: Session):
    """Get user statistics"""
    total_users = db.query(func.count(models.User.id)).scalar() or 0
    users_with_orders = db.query(func.count(func.distinct(models.Order.user_id))).scalar() or 0
    
    return {
        "total_users": total_users,
        "users_with_orders": users_with_orders,
        "users_without_orders": total_users - users_with_orders
    }


def get_order_stats(db: Session):
    """Get order statistics"""
    total_orders = db.query(func.count(models.Order.id)).scalar() or 0
    total_amount = db.query(func.sum(models.Order.amount)).scalar() or 0
    avg_amount = db.query(func.avg(models.Order.amount)).scalar() or 0
    max_amount = db.query(func.max(models.Order.amount)).scalar() or 0
    min_amount = db.query(func.min(models.Order.amount)).scalar() or 0
    
    return {
        "total_orders": total_orders,
        "total_amount": float(total_amount) if total_amount else 0,
        "avg_amount": float(avg_amount) if avg_amount else 0,
        "max_amount": float(max_amount) if max_amount else 0,
        "min_amount": float(min_amount) if min_amount else 0
    }


def get_top_products(db: Session, limit: int = 10):
    """Get top products by order count"""
    products = db.query(
        models.Order.product,
        func.count(models.Order.id).label('order_count'),
        func.sum(models.Order.amount).label('total_amount'),
        func.avg(models.Order.amount).label('avg_amount')
    ).group_by(models.Order.product).order_by(func.count(models.Order.id).desc()).limit(limit).all()
    
    return [
        {
            "product": product.product,
            "order_count": product.order_count,
            "total_amount": float(product.total_amount) if product.total_amount else 0,
            "avg_amount": float(product.avg_amount) if product.avg_amount else 0
        }
        for product in products
    ]


def get_user_orders(db: Session, user_id: int, limit: int = 10):
    """Get orders for a specific user"""
    orders = db.query(models.Order).filter(
        models.Order.user_id == user_id
    ).order_by(models.Order.created_at.desc()).limit(limit).all()
    
    return [
        {
            "id": order.id,
            "product": order.product,
            "amount": order.amount,
            "created_at": order.created_at.isoformat() if order.created_at else None
        }
        for order in orders
    ]


def get_average_order_value(db: Session):
    """Get average order value"""
    avg = db.query(func.avg(models.Order.amount)).scalar() or 0
    return {
        "average_order_value": float(avg)
    }


def get_sales_by_product(db: Session, limit: int = 10):
    """Get sales statistics by product"""
    sales_by_product = db.query(
        models.Order.product,
        func.count(models.Sale.id).label('sale_count'),
        func.sum(models.Sale.revenue).label('total_revenue'),
        func.avg(models.Sale.revenue).label('avg_revenue')
    ).join(
        models.Sale, models.Sale.order_id == models.Order.id
    ).group_by(models.Order.product).order_by(
        func.sum(models.Sale.revenue).desc()
    ).limit(limit).all()
    
    return [
        {
            "product": item.product,
            "sale_count": item.sale_count,
            "total_revenue": float(item.total_revenue) if item.total_revenue else 0,
            "avg_revenue": float(item.avg_revenue) if item.avg_revenue else 0
        }
        for item in sales_by_product
    ]


def search_orders(db: Session, product: Optional[str] = None, min_amount: Optional[float] = None, 
                  max_amount: Optional[float] = None, limit: int = 20):
    """Search orders by product name or amount range"""
    query = db.query(models.Order)
    
    if product:
        query = query.filter(models.Order.product.ilike(f"%{product}%"))
    
    if min_amount is not None:
        query = query.filter(models.Order.amount >= min_amount)
    
    if max_amount is not None:
        query = query.filter(models.Order.amount <= max_amount)
    
    orders = query.order_by(models.Order.created_at.desc()).limit(limit).all()
    
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


def get_user_by_id(db: Session, user_id: int):
    """Get user information by ID"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return None
    
    order_count = db.query(func.count(models.Order.id)).filter(
        models.Order.user_id == user_id
    ).scalar() or 0
    
    total_spent = db.query(func.sum(models.Order.amount)).filter(
        models.Order.user_id == user_id
    ).scalar() or 0
    
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "order_count": order_count,
        "total_spent": float(total_spent)
    }


def get_revenue_by_period(db: Session, days: int = 30):
    """Get revenue statistics for the last N days"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    total_revenue = db.query(func.sum(models.Sale.revenue)).filter(
        models.Sale.created_at >= cutoff_date
    ).scalar() or 0
    
    sale_count = db.query(func.count(models.Sale.id)).filter(
        models.Sale.created_at >= cutoff_date
    ).scalar() or 0
    
    avg_revenue = db.query(func.avg(models.Sale.revenue)).filter(
        models.Sale.created_at >= cutoff_date
    ).scalar() or 0
    
    return {
        "period_days": days,
        "total_revenue": float(total_revenue),
        "sale_count": sale_count,
        "avg_revenue": float(avg_revenue) if avg_revenue else 0
    }


def get_orders_by_date_range(db: Session, start_date: Optional[str] = None, 
                              end_date: Optional[str] = None, limit: int = 50):
    """Get orders within a date range"""
    query = db.query(models.Order)
    
    if start_date:
        try:
            start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(models.Order.created_at >= start)
        except:
            pass
    
    if end_date:
        try:
            end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(models.Order.created_at <= end)
        except:
            pass
    
    orders = query.order_by(models.Order.created_at.desc()).limit(limit).all()
    
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
