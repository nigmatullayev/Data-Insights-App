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
    
    if tool_name == "get_row_count":
        # Simple number - can show as stat card
        response["visualization"] = {
            "type": "stat",
            "value": result
        }
    elif tool_name == "get_recent_records":
        # Table data
        if isinstance(result, list) and len(result) > 0:
            response["visualization"] = {
                "type": "table",
                "data": result,
                "columns": list(result[0].keys()) if result else []
            }
    elif tool_name == "get_sales_stats":
        # Can show as bar chart or pie chart
        if isinstance(result, dict):
            response["visualization"] = {
                "type": "chart",
                "chart_type": "bar",  # or "pie"
                "data": result,
                "labels": list(result.keys()),
                "values": list(result.values())
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
                    "description": "Get total number of rows from a table",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "table": {
                                "type": "string",
                                "enum": ["users", "orders", "sales"]
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
                    "description": "Get most recent records from a table",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "table": {
                                "type": "string",
                                "enum": ["orders", "sales"]
                            },
                            "limit": {
                                "type": "integer",
                                "default": 5,
                                "minimum": 1,
                                "maximum": 100
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
                    "description": "Get aggregated sales statistics",
                    "parameters": {
                        "type": "object",
                        "properties": {}
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
                            "You are a data analytics assistant. "
                            "You must NOT access database directly. "
                            "You must use provided tools to answer questions. "
                            "Always provide clear and helpful responses based on the data you receive."
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
