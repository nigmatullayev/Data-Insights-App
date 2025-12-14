import json
from cerebras.cloud.sdk import Cerebras
from app.services import tools
from app.core.config import settings
from app.core.safety import validate_table_name, sanitize_input
from typing import Dict, Any, Optional

client = Cerebras(
    api_key=settings.CEREBRAS_API_KEY
)

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
    try:
        # Sanitize input
        sanitized_message = sanitize_input(message)
        
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
    
    except Exception as e:
        return {
            "error": f"Error processing request: {str(e)}",
            "message": "Please try again or contact support if the issue persists."
        }
