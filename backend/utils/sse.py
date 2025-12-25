"""
Server-Sent Events (SSE) formatting utilities.
"""
import json
from typing import Any


def format_sse(event_data: dict[str, Any]) -> str:
    """
    Format a dictionary as an SSE data line.
    
    Returns a string in the format: "data: {json}\n\n"
    
    Args:
        event_data: Dictionary to serialize as JSON
        
    Returns:
        Formatted SSE data string
    """
    # Use ensure_ascii=False to properly encode Hebrew characters
    json_str = json.dumps(event_data, ensure_ascii=False)
    return f"data: {json_str}\n\n"


def format_sse_comment(comment: str) -> str:
    """
    Format a comment line for SSE (useful for keep-alive).
    
    Args:
        comment: Comment text
        
    Returns:
        Formatted SSE comment string
    """
    return f": {comment}\n\n"

