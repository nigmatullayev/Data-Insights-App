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
                "table": {
                    "type": "string",
                    "enum": ["orders", "sales"],
                    "required": True,
                    "description": "Name of the table"
                },
                "limit": {
                    "type": "integer",
                    "default": 5,
                    "required": False,
                    "description": "Number of records to return"
                }
            },
            "returns": "array - List of recent records"
        },
        {
            "name": "get_sales_stats",
            "description": "Get aggregated sales statistics",
            "parameters": {},
            "returns": "object - Sales statistics (total_sales, avg_sales, max_sale)"
        }
    ]
    
    return {
        "tools": tools,
        "count": len(tools),
        "description": "Available functions that the AI agent can use to query the database"
    }

