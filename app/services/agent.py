import json
import openai
from app.services import tools

openai.api_key = "YOUR_API_KEY"

def chat_with_agent(message: str, db):
    functions = [
        {
            "name": "get_row_count",
            "description": "Get total row count from a table",
            "parameters": {
                "type": "object",
                "properties": {
                    "table": {"type": "string"}
                },
                "required": ["table"]
            }
        },
        {
            "name": "get_recent_records",
            "description": "Get recent records from table",
            "parameters": {
                "type": "object",
                "properties": {
                    "table": {"type": "string"},
                    "limit": {"type": "integer"}
                },
                "required": ["table"]
            }
        },
        {
            "name": "get_sales_stats",
            "description": "Get sales statistics",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": message}],
        functions=functions,
        function_call="auto"
    )

    msg = response["choices"][0]["message"]

    if msg.get("function_call"):
        name = msg["function_call"]["name"]
        args = json.loads(msg["function_call"]["arguments"])

        result = getattr(tools, name)(db, **args)
        return {"tool": name, "result": result}

    return {"answer": msg["content"]}
