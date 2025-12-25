"""
Prescription-related tools for the pharmacy assistant.
"""
from typing import Optional, Literal
from datetime import date
from repositories import prescription_repo, user_repo
from tools.errors import tool_success, tool_error, ToolErrorCode
from logging_config import get_logger

logger = get_logger(__name__)


def list_user_prescriptions(
    user_id: int,
    status: Optional[Literal["active", "expired", "all"]] = "active"
) -> dict:
    """
    List prescriptions for a user.
    
    Args:
        user_id: User ID to look up prescriptions for
        status: Filter by status - "active" (default), "expired", or "all"
        
    Returns:
        List of prescriptions with refill information
    """
    logger.info("tool_list_user_prescriptions", user_id=user_id, status=status)
    
    # Verify user exists
    user = user_repo.get_user_by_id(user_id)
    if not user:
        return tool_error(
            ToolErrorCode.NOT_FOUND, 
            f"User with ID {user_id} not found"
        )
    
    # Get prescriptions based on status filter
    today = date.today().isoformat()
    
    if status == "active":
        prescriptions = prescription_repo.get_prescriptions_by_user_id(user_id, active_only=True)
    else:
        all_prescriptions = prescription_repo.get_prescriptions_by_user_id(user_id, active_only=False)
        if status == "expired":
            prescriptions = [p for p in all_prescriptions if p["expiry_date"] < today]
        else:  # "all"
            prescriptions = all_prescriptions
    
    # Format prescriptions
    formatted = []
    for p in prescriptions:
        refills_remaining = p["refills_allowed"] - p["refills_used"]
        is_expired = p["expiry_date"] < today
        
        formatted.append({
            "prescription_id": p["id"],
            "medication_name": p["medication_name"],
            "medication_name_he": p["medication_hebrew_name"],
            "prescribed_date": p["prescribed_date"],
            "expiry_date": p["expiry_date"],
            "is_expired": is_expired,
            "refills_allowed": p["refills_allowed"],
            "refills_used": p["refills_used"],
            "refills_remaining": refills_remaining,
            "can_refill": not is_expired and refills_remaining > 0,
            "prescribing_doctor": p["prescribing_doctor"]
        })
    
    data = {
        "user_id": user_id,
        "user_name": user["name"],
        "filter": status,
        "prescriptions": formatted,
        "count": len(formatted)
    }
    
    return tool_success(data)


def request_prescription_refill(
    user_id: int,
    prescription_id: int
) -> dict:
    """
    Request a refill for an existing prescription.
    
    Args:
        user_id: User ID requesting the refill
        prescription_id: Prescription ID to refill
        
    Returns:
        Refill request status and confirmation
    """
    logger.info("tool_request_prescription_refill", user_id=user_id, prescription_id=prescription_id)
    
    # Verify user exists
    user = user_repo.get_user_by_id(user_id)
    if not user:
        return tool_error(
            ToolErrorCode.NOT_FOUND, 
            f"User with ID {user_id} not found"
        )
    
    # Validate prescription
    is_valid, error_message = prescription_repo.is_prescription_valid(prescription_id, user_id)
    
    if not is_valid:
        # Map error message to appropriate code
        if "not found" in error_message.lower():
            code = ToolErrorCode.NOT_FOUND
        elif "expired" in error_message.lower():
            code = ToolErrorCode.EXPIRED
        elif "no refills" in error_message.lower():
            code = ToolErrorCode.NO_REFILLS
        elif "does not belong" in error_message.lower():
            code = ToolErrorCode.UNAUTHORIZED
        else:
            code = ToolErrorCode.INVALID_INPUT
        
        return tool_error(code, error_message)
    
    # Get prescription details for confirmation
    prescription = prescription_repo.get_prescription_by_id(prescription_id)
    
    # Create the refill request
    request_id = prescription_repo.create_refill_request(user_id, prescription_id)
    
    if not request_id:
        return tool_error(
            ToolErrorCode.INTERNAL_ERROR, 
            "Failed to create refill request. Please try again."
        )
    
    # Increment refills used
    prescription_repo.increment_refills_used(prescription_id)
    
    # Calculate remaining refills after this request
    new_refills_remaining = (
        prescription["refills_allowed"] - prescription["refills_used"] - 1
    )
    
    data = {
        "request_id": request_id,
        "status": "pending",
        "message": (
            f"Refill request #{request_id} submitted successfully for "
            f"{prescription['medication_name']}. "
            f"It will be ready for pickup in 2-3 hours."
        ),
        "prescription_id": prescription_id,
        "medication_name": prescription["medication_name"],
        "medication_name_he": prescription["medication_hebrew_name"],
        "refills_remaining_after": new_refills_remaining,
        "user_name": user["name"]
    }
    
    return tool_success(data)

