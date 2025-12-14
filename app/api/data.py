"""
Data summary and statistics endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import get_db
from app.db import models

router = APIRouter()

@router.get("/data/summary")
def get_data_summary(db: Session = Depends(get_db)):
    """
    Get database statistics summary
    """
    try:
        user_count = db.query(func.count(models.User.id)).scalar() or 0
        order_count = db.query(func.count(models.Order.id)).scalar() or 0
        sale_count = db.query(func.count(models.Sale.id)).scalar() or 0
        
        total_revenue = db.query(func.sum(models.Sale.revenue)).scalar() or 0
        avg_order_amount = db.query(func.avg(models.Order.amount)).scalar() or 0
        avg_sale_revenue = db.query(func.avg(models.Sale.revenue)).scalar() or 0
        
        return {
            "tables": {
                "users": {
                    "count": user_count
                },
                "orders": {
                    "count": order_count,
                    "avg_amount": float(avg_order_amount) if avg_order_amount else 0
                },
                "sales": {
                    "count": sale_count,
                    "total_revenue": float(total_revenue) if total_revenue else 0,
                    "avg_revenue": float(avg_sale_revenue) if avg_sale_revenue else 0
                }
            },
            "summary": {
                "total_users": user_count,
                "total_orders": order_count,
                "total_sales": sale_count,
                "total_revenue": float(total_revenue) if total_revenue else 0
            }
        }
    except Exception as e:
        return {"error": str(e)}

