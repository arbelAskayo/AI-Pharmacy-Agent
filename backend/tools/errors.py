"""
Standardized error types for tool responses.
"""
from enum import Enum
from typing import Any


class ToolErrorCode(str, Enum):
    """Standardized error codes for tool execution."""
    NOT_FOUND = "NOT_FOUND"
    AMBIGUOUS = "AMBIGUOUS"
    OUT_OF_STOCK = "OUT_OF_STOCK"
    INVALID_INPUT = "INVALID_INPUT"
    EXPIRED = "EXPIRED"
    NO_REFILLS = "NO_REFILLS"
    UNAUTHORIZED = "UNAUTHORIZED"
    INTERNAL_ERROR = "INTERNAL_ERROR"


def tool_success(data: Any) -> dict:
    """Create a successful tool response."""
    return {
        "success": True,
        "data": data
    }


def tool_error(code: ToolErrorCode, message: str) -> dict:
    """Create an error tool response."""
    return {
        "success": False,
        "error": {
            "code": code.value,
            "message": message
        }
    }

