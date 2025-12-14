"""
Tools/Function listing endpoint
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/tools")
def get_tools():
    """
    Get list of available tools/functions
    """
    tools = [
        {
            "name": "get_row_count",
            "description": "Get total number of rows from a table",
            "parameters": {
                "table": {
                    "type": "string",
                    "enum": ["users", "orders", "sales"],
                    "required": True,
                    "description": "Name of the table to count rows"
                }
            },
            "returns": "integer - Total number of rows"
        },
        {
            "name": "get_recent_records",
            "description": "Get most recent records from a table",
            "parameters": {
                "table": {"type": "string", "enum": ["orders", "sales"], "required": True},
                "limit": {"type": "integer", "default": 5, "required": False}
            },
            "returns": "array - List of recent records"
        },
        {
            "name": "get_sales_stats",
            "description": "Get aggregated sales statistics",
            "parameters": {},
            "returns": "object - Sales statistics"
        },
        {
            "name": "get_user_stats",
            "description": "Get user statistics (total users, users with orders, etc.)",
            "parameters": {},
            "returns": "object - User statistics"
        },
        {
            "name": "get_order_stats",
            "description": "Get order statistics (total orders, amounts, averages)",
            "parameters": {},
            "returns": "object - Order statistics"
        },
        {
            "name": "get_top_products",
            "description": "Get top products by order count",
            "parameters": {
                "limit": {"type": "integer", "default": 10, "required": False}
            },
            "returns": "array - Top products list"
        },
        {
            "name": "get_user_orders",
            "description": "Get orders for a specific user",
            "parameters": {
                "user_id": {"type": "integer", "required": True},
                "limit": {"type": "integer", "default": 10, "required": False}
            },
            "returns": "array - User orders list"
        },
        {
            "name": "get_average_order_value",
            "description": "Get average order value",
            "parameters": {},
            "returns": "object - Average order value"
        },
        {
            "name": "get_sales_by_product",
            "description": "Get sales statistics grouped by product",
            "parameters": {
                "limit": {"type": "integer", "default": 10, "required": False}
            },
            "returns": "array - Sales by product"
        },
        {
            "name": "search_orders",
            "description": "Search orders by product name or amount range",
            "parameters": {
                "product": {"type": "string", "required": False},
                "min_amount": {"type": "number", "required": False},
                "max_amount": {"type": "number", "required": False},
                "limit": {"type": "integer", "default": 20, "required": False}
            },
            "returns": "array - Search results"
        },
        {
            "name": "get_user_by_id",
            "description": "Get user information by user ID",
            "parameters": {
                "user_id": {"type": "integer", "required": True}
            },
            "returns": "object - User information"
        },
        {
            "name": "get_revenue_by_period",
            "description": "Get revenue statistics for the last N days",
            "parameters": {
                "days": {"type": "integer", "default": 30, "required": False}
            },
            "returns": "object - Revenue statistics"
        },
        {
            "name": "get_orders_by_date_range",
            "description": "Get orders within a specific date range",
            "parameters": {
                "start_date": {"type": "string", "required": False},
                "end_date": {"type": "string", "required": False},
                "limit": {"type": "integer", "default": 50, "required": False}
            },
            "returns": "array - Orders in date range"
        }
    ]
    
    return {
        "tools": tools,
        "count": len(tools),
        "description": "Available functions that the AI agent can use to query the database"
    }

