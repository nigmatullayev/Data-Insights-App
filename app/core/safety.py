"""
Safety mechanisms to prevent dangerous database operations
"""
import re
from typing import List

DANGEROUS_KEYWORDS = [
    "DELETE", "DROP", "TRUNCATE", "ALTER", "CREATE", "INSERT", "UPDATE",
    "EXEC", "EXECUTE", "GRANT", "REVOKE", "SHUTDOWN", "KILL"
]

def is_dangerous_query(query: str) -> bool:
    """
    Check if a query contains dangerous SQL operations
    """
    if not query:
        return False
    
    query_upper = query.upper().strip()
    
    # Check for dangerous keywords
    for keyword in DANGEROUS_KEYWORDS:
        # Use word boundary to avoid false positives
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, query_upper):
            return True
    
    return False

def sanitize_input(input_str: str) -> str:
    """
    Basic input sanitization
    """
    if not input_str:
        return ""
    
    # Remove potentially dangerous characters
    dangerous_chars = [';', '--', '/*', '*/', 'xp_', 'sp_']
    sanitized = input_str
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    
    return sanitized.strip()

def validate_table_name(table: str) -> bool:
    """
    Validate that table name is in allowed list
    """
    ALLOWED_TABLES = ["users", "orders", "sales"]
    return table.lower() in ALLOWED_TABLES

