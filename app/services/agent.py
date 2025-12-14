import json
import logging
from cerebras.cloud.sdk import Cerebras
from app.services import tools
from app.core.config import settings
from app.core.safety import validate_table_name, sanitize_input
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Initialize client with error handling
def get_cerebras_client():
    """
    Get or create Cerebras client with proper error handling
    """
    if not settings.CEREBRAS_API_KEY:
        raise ValueError("CEREBRAS_API_KEY is not set in environment variables")
    
    try:
        # Use the same pattern as Cerebras documentation
        client = Cerebras(api_key=settings.CEREBRAS_API_KEY)
        return client
    except Exception as e:
        logger.error(f"Failed to initialize Cerebras client: {str(e)}")
        raise ValueError(f"Failed to initialize Cerebras client: {str(e)}")

# Initialize client at module level (lazy initialization)
# Don't initialize at startup to avoid errors if API key is missing
client = None

def format_response_for_visualization(result: Any, tool_name: str) -> Dict[str, Any]:
    """
    Format response for frontend visualization (tables, charts)
    """
    response = {
        "tool_used": tool_name,
        "result": result,
        "visualization": None
    }
    
    # Stat cards (single number)
    if tool_name in ["get_row_count", "get_average_order_value"]:
        if isinstance(result, dict):
            # For dict results, show first value
            value = list(result.values())[0] if result else 0
        else:
            value = result
        response["visualization"] = {
            "type": "stat",
            "value": value
        }
    
    # Table data (lists)
    elif tool_name in ["get_recent_records", "get_user_orders", "get_top_products", 
                       "get_sales_by_product", "search_orders", "get_orders_by_date_range"]:
        if isinstance(result, list) and len(result) > 0:
            response["visualization"] = {
                "type": "table",
                "data": result,
                "columns": list(result[0].keys()) if result else []
            }
    
    # Charts (dictionaries with multiple values)
    elif tool_name in ["get_sales_stats", "get_user_stats", "get_order_stats", 
                       "get_revenue_by_period", "get_user_by_id"]:
        if isinstance(result, dict):
            # Filter out non-numeric values for charts
            numeric_data = {k: v for k, v in result.items() if isinstance(v, (int, float))}
            if len(numeric_data) > 0:
                response["visualization"] = {
                    "type": "chart",
                    "chart_type": "bar",
                    "data": result,
                    "labels": list(numeric_data.keys()),
                    "values": list(numeric_data.values())
                }
            else:
                # If no numeric data, show as table
                response["visualization"] = {
                    "type": "table",
                    "data": [result],
                    "columns": list(result.keys())
                }
    
    return response

def chat_with_agent(message: str, db) -> Dict[str, Any]:
    """
    Cerebras-powered AI agent.
    LLM NEVER sees database.
    Only function calling allowed.
    """
    global client
    
    try:
        # Check if client is initialized
        if client is None:
            try:
                client = get_cerebras_client()
            except Exception as e:
                return {
                    "error": f"Cerebras API client is not available: {str(e)}",
                    "message": "Please check your CEREBRAS_API_KEY in .env file"
                }
        
        # Check API key
        if not settings.CEREBRAS_API_KEY:
            return {
                "error": "CEREBRAS_API_KEY is not configured",
                "message": "Please set CEREBRAS_API_KEY in your .env file"
            }
        
        # Sanitize input
        sanitized_message = sanitize_input(message)
        
        if not sanitized_message:
            return {
                "error": "Empty or invalid message",
                "message": "Please provide a valid question"
            }
        
        tools_schema = [
            {
                "type": "function",
                "function": {
                    "name": "get_row_count",
                    "description": "Get total number of rows from a table. Use this when user asks 'Nechta foydalanuvchi bor?', 'Jami nechta buyurtma?', 'Nechta savdo bor?' or similar questions about counting records.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "table": {
                                "type": "string",
                                "enum": ["users", "orders", "sales"],
                                "description": "Table name: 'users' for foydalanuvchilar, 'orders' for buyurtmalar, 'sales' for savdolar"
                            }
                        },
                        "required": ["table"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_recent_records",
                    "description": "Get most recent records from a table. Use this when user asks 'Oxirgi 10 ta buyurtma', 'So'nggi savdolar', 'Eng yangi yozuvlar' or similar questions about recent records.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "table": {
                                "type": "string",
                                "enum": ["orders", "sales"],
                                "description": "Table name: 'orders' for buyurtmalar, 'sales' for savdolar"
                            },
                            "limit": {
                                "type": "integer",
                                "default": 5,
                                "minimum": 1,
                                "maximum": 100,
                                "description": "Number of records to return (nechta yozuv)"
                            }
                        },
                        "required": ["table"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_sales_stats",
                    "description": "Get aggregated sales statistics including total sales, average sales, maximum and minimum sale. Use this when user asks 'Savdo statistikasi', 'Daromad ma'lumotlari', 'Savdo ko'rsatkichlari' or similar questions about sales statistics.",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_user_stats",
                    "description": "Get user statistics including total users, users with orders, users without orders. Use this when user asks 'Foydalanuvchilar statistikasi', 'Nechta foydalanuvchi buyurtma bergan?', 'Foydalanuvchilar haqida ma'lumot' or similar questions.",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_order_stats",
                    "description": "Get order statistics including total orders, total amount, average amount, max and min amounts. Use this when user asks 'Buyurtmalar statistikasi', 'Jami buyurtma summasi', 'O'rtacha buyurtma qiymati' or similar questions.",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_top_products",
                    "description": "Get top products by order count. Use this when user asks 'Eng ko'p sotilgan mahsulotlar', 'Top 10 mahsulot', 'Qaysi mahsulot ko'p sotilgan?' or similar questions.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "limit": {
                                "type": "integer",
                                "default": 10,
                                "minimum": 1,
                                "maximum": 50,
                                "description": "Number of top products to return"
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_user_orders",
                    "description": "Get orders for a specific user by user ID. Use this when user asks 'Foydalanuvchi buyurtmalari', 'ID 5 foydalanuvchining buyurtmalari', 'Foydalanuvchi nechta buyurtma bergan?' or similar questions.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "integer",
                                "description": "User ID (foydalanuvchi ID raqami)"
                            },
                            "limit": {
                                "type": "integer",
                                "default": 10,
                                "minimum": 1,
                                "maximum": 100,
                                "description": "Number of orders to return"
                            }
                        },
                        "required": ["user_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_average_order_value",
                    "description": "Get average order value. Use this when user asks 'O'rtacha buyurtma qiymati', 'Bir buyurtmaning o'rtacha summasi' or similar questions.",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_sales_by_product",
                    "description": "Get sales statistics grouped by product. Use this when user asks 'Mahsulot bo'yicha savdo', 'Qaysi mahsulot ko'p daromad keltiradi?', 'Mahsulotlar daromadi' or similar questions.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "limit": {
                                "type": "integer",
                                "default": 10,
                                "minimum": 1,
                                "maximum": 50,
                                "description": "Number of products to return"
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_orders",
                    "description": "Search orders by product name or amount range. Use this when user asks 'Mahsulot bo'yicha qidirish', '100 dollardan yuqori buyurtmalar', 'Laptop buyurtmalari' or similar questions.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "product": {
                                "type": "string",
                                "description": "Product name to search (mahsulot nomi)"
                            },
                            "min_amount": {
                                "type": "number",
                                "description": "Minimum order amount (minimal buyurtma summasi)"
                            },
                            "max_amount": {
                                "type": "number",
                                "description": "Maximum order amount (maksimal buyurtma summasi)"
                            },
                            "limit": {
                                "type": "integer",
                                "default": 20,
                                "minimum": 1,
                                "maximum": 100,
                                "description": "Number of results to return"
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_user_by_id",
                    "description": "Get user information by user ID including name, email, order count, total spent. Use this when user asks 'Foydalanuvchi ma'lumotlari', 'ID 5 foydalanuvchi kim?', 'Foydalanuvchi necha pul sarflagan?' or similar questions.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "integer",
                                "description": "User ID (foydalanuvchi ID raqami)"
                            }
                        },
                        "required": ["user_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_revenue_by_period",
                    "description": "Get revenue statistics for the last N days. Use this when user asks 'Oxirgi 30 kunlik daromad', 'Haftalik daromad', 'So'nggi oy statistikasi' or similar questions.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "days": {
                                "type": "integer",
                                "default": 30,
                                "minimum": 1,
                                "maximum": 365,
                                "description": "Number of days to look back (necha kun oldin)"
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_orders_by_date_range",
                    "description": "Get orders within a specific date range. Use this when user asks '2024 yil buyurtmalari', 'Sana oralig'idagi buyurtmalar', 'Oxirgi hafta buyurtmalari' or similar questions.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "start_date": {
                                "type": "string",
                                "description": "Start date in ISO format (boshlanish sanasi, masalan: 2024-01-01)"
                            },
                            "end_date": {
                                "type": "string",
                                "description": "End date in ISO format (tugash sanasi, masalan: 2024-12-31)"
                            },
                            "limit": {
                                "type": "integer",
                                "default": 50,
                                "minimum": 1,
                                "maximum": 200,
                                "description": "Number of orders to return"
                            }
                        }
                    }
                }
            }
        ]

        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a data analytics assistant that understands and responds in Uzbek language. "
                            "You must understand questions in Uzbek (O'zbek tili) and respond in Uzbek. "
                            "You must NOT access database directly. "
                            "You must use provided tools to answer questions. "
                            "Always provide clear and helpful responses in Uzbek language based on the data you receive. "
                            "When users ask questions in Uzbek like 'Nechta foydalanuvchi bor?' or 'Oxirgi 10 ta buyurtma', "
                            "understand them correctly and use the appropriate tools. "
                            "Respond in Uzbek language, using proper Uzbek grammar and terminology."
                        )
                    },
                    {"role": "user", "content": sanitized_message}
                ],
                tools=tools_schema,
                tool_choice="auto"
            )
        except Exception as api_error:
            error_msg = str(api_error)
            logger.error(f"Cerebras API error: {error_msg}")
            
            # Provide more specific error messages
            if "Connection" in error_msg or "connection" in error_msg.lower():
                return {
                    "error": "Connection error with Cerebras API",
                    "message": "Please check your internet connection and API key. If the problem persists, the API service might be temporarily unavailable.",
                    "details": "Unable to connect to Cerebras API service"
                }
            elif "401" in error_msg or "Unauthorized" in error_msg or "authentication" in error_msg.lower():
                return {
                    "error": "Authentication failed",
                    "message": "Invalid API key. Please check your CEREBRAS_API_KEY in .env file"
                }
            elif "429" in error_msg or "rate limit" in error_msg.lower():
                return {
                    "error": "Rate limit exceeded",
                    "message": "Too many requests. Please wait a moment and try again."
                }
            else:
                return {
                    "error": f"API error: {error_msg}",
                    "message": "An error occurred while processing your request. Please try again."
                }

        msg = response.choices[0].message

        # Tool chaqirilsa
        if msg.tool_calls:
            call = msg.tool_calls[0]
            tool_name = call.function.name
            args = json.loads(call.function.arguments)
            
            # Safety check - validate table name if present
            if "table" in args:
                if not validate_table_name(args["table"]):
                    return {
                        "error": "Invalid table name. Allowed tables: users, orders, sales",
                        "tool_used": tool_name
                    }
            
            # Safety check - validate limit
            if "limit" in args:
                limit = args.get("limit", 5)
                if limit < 1 or limit > 100:
                    args["limit"] = min(max(limit, 1), 100)
            
            try:
                result = getattr(tools, tool_name)(db, **args)
                formatted_response = format_response_for_visualization(result, tool_name)
                
                # Add AI explanation if available
                if msg.content:
                    formatted_response["explanation"] = msg.content
                
                return formatted_response
            except AttributeError:
                return {
                    "error": f"Tool '{tool_name}' not found",
                    "available_tools": ["get_row_count", "get_recent_records", "get_sales_stats"]
                }
            except Exception as e:
                return {
                    "error": f"Error executing tool: {str(e)}",
                    "tool_used": tool_name
                }

        return {
            "answer": msg.content,
            "tool_used": None
        }
    
    except ValueError as ve:
        return {
            "error": str(ve),
            "message": "Configuration error. Please check your settings."
        }
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Unexpected error in chat_with_agent: {error_msg}")
        return {
            "error": f"Error processing request: {error_msg}",
            "message": "Please try again or contact support if the issue persists.",
            "type": type(e).__name__
        }
