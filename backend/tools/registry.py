"""
Tool registry for OpenAI function calling.
Provides the tools schema and maps tool names to their implementations.
"""
from typing import Callable, Any
from tools.medication_tools import (
    get_medication_by_name,
    check_medication_stock,
    get_prescription_requirement
)
from tools.user_tools import get_user_profile
from tools.prescription_tools import (
    list_user_prescriptions,
    request_prescription_refill
)


# OpenAI function schemas for tool calling
TOOLS_SCHEMA: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "get_medication_by_name",
            "description": (
                "Get detailed information about a medication including its active ingredient, "
                "dosage form, strength, usage instructions, and whether it requires a prescription. "
                "Use this when a user asks about a specific medication."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the medication in English or Hebrew"
                    },
                    "lang": {
                        "type": "string",
                        "enum": ["en", "he"],
                        "description": "Preferred language for the response. Use 'he' if user speaks Hebrew."
                    }
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_medication_stock",
            "description": (
                "Check the current stock availability of a medication across pharmacy branches. "
                "Returns quantity available at each branch. Use when user asks about availability "
                "or wants to know if a medication is in stock."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "medication_name": {
                        "type": "string",
                        "description": "The name of the medication to check stock for"
                    },
                    "branch": {
                        "type": "string",
                        "description": "Optional: specific branch to check (e.g., 'Main Street', 'Downtown', 'Airport')"
                    }
                },
                "required": ["medication_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_prescription_requirement",
            "description": (
                "Check if a medication requires a prescription or is available over-the-counter. "
                "Use when user asks if they need a prescription for a medication."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "medication_name": {
                        "type": "string",
                        "description": "The name of the medication to check"
                    }
                },
                "required": ["medication_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_user_profile",
            "description": (
                "Look up a user's profile by their ID, phone number, or email. "
                "Use this to identify a customer before performing actions like prescription lookup or refill requests. "
                "Ask the user to provide their phone or email if not already known."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "integer",
                        "description": "The user's ID if already known"
                    },
                    "phone": {
                        "type": "string",
                        "description": "User's phone number to search by"
                    },
                    "email": {
                        "type": "string",
                        "description": "User's email address to search by"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_user_prescriptions",
            "description": (
                "List all prescriptions for a user, including medication name, expiry date, "
                "and remaining refills. User must be identified first using get_user_profile. "
                "Use when user asks about their prescriptions or wants to see what they can refill."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "integer",
                        "description": "The user's ID (obtained from get_user_profile)"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["active", "expired", "all"],
                        "description": "Filter prescriptions by status. Default is 'active'."
                    }
                },
                "required": ["user_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "request_prescription_refill",
            "description": (
                "Submit a refill request for an existing prescription. "
                "Validates that the prescription is active and has refills remaining. "
                "User must be identified first. Use when user wants to refill a prescription."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "integer",
                        "description": "The user's ID (obtained from get_user_profile)"
                    },
                    "prescription_id": {
                        "type": "integer",
                        "description": "The prescription ID to refill (obtained from list_user_prescriptions)"
                    }
                },
                "required": ["user_id", "prescription_id"]
            }
        }
    }
]


# Mapping from tool name to callable
TOOL_FUNCTIONS: dict[str, Callable[..., dict]] = {
    "get_medication_by_name": get_medication_by_name,
    "check_medication_stock": check_medication_stock,
    "get_prescription_requirement": get_prescription_requirement,
    "get_user_profile": get_user_profile,
    "list_user_prescriptions": list_user_prescriptions,
    "request_prescription_refill": request_prescription_refill,
}


def get_tool_names() -> list[str]:
    """Get list of all available tool names."""
    return list(TOOL_FUNCTIONS.keys())


def execute_tool(tool_name: str, arguments: dict) -> dict:
    """
    Execute a tool by name with the given arguments.
    
    Args:
        tool_name: Name of the tool to execute
        arguments: Dictionary of arguments to pass to the tool
        
    Returns:
        Tool result dictionary
    """
    if tool_name not in TOOL_FUNCTIONS:
        return {
            "success": False,
            "error": {
                "code": "UNKNOWN_TOOL",
                "message": f"Unknown tool: {tool_name}"
            }
        }
    
    try:
        func = TOOL_FUNCTIONS[tool_name]
        return func(**arguments)
    except TypeError as e:
        return {
            "success": False,
            "error": {
                "code": "INVALID_ARGUMENTS",
                "message": f"Invalid arguments for {tool_name}: {str(e)}"
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "EXECUTION_ERROR",
                "message": f"Error executing {tool_name}: {str(e)}"
            }
        }

