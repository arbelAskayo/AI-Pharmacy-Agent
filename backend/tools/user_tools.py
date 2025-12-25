"""
User-related tools for the pharmacy assistant.
"""
from typing import Optional
from repositories import user_repo
from tools.errors import tool_success, tool_error, ToolErrorCode
from logging_config import get_logger

logger = get_logger(__name__)


def get_user_profile(
    user_id: Optional[int] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None
) -> dict:
    """
    Get user profile information.
    Can search by user_id, phone, or email.
    
    Args:
        user_id: User ID (if known)
        phone: Phone number to search
        email: Email address to search
        
    Returns:
        User profile data or error
    """
    logger.info("tool_get_user_profile", user_id=user_id, phone=phone, email=email)
    
    # Validate input - at least one identifier required
    if not user_id and not phone and not email:
        return tool_error(
            ToolErrorCode.INVALID_INPUT, 
            "Please provide at least one of: user_id, phone number, or email"
        )
    
    user = None
    
    # Try user_id first if provided
    if user_id:
        user = user_repo.get_user_by_id(user_id)
        if not user:
            return tool_error(
                ToolErrorCode.NOT_FOUND, 
                f"User with ID {user_id} not found"
            )
    
    # Try phone number
    elif phone:
        user = user_repo.find_user_by_search_term(phone)
        if not user:
            return tool_error(
                ToolErrorCode.NOT_FOUND, 
                f"No user found with phone number matching '{phone}'"
            )
    
    # Try email
    elif email:
        user = user_repo.find_user_by_search_term(email)
        if not user:
            return tool_error(
                ToolErrorCode.NOT_FOUND, 
                f"No user found with email matching '{email}'"
            )
    
    data = {
        "id": user["id"],
        "name": user["name"],
        "name_he": user["hebrew_name"],
        "phone": user["phone"],
        "email": user["email"]
    }
    
    return tool_success(data)

