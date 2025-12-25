"""
Medication-related tools for the pharmacy assistant.
"""
from typing import Optional, Literal
from repositories import medication_repo, stock_repo
from tools.errors import tool_success, tool_error, ToolErrorCode
from logging_config import get_logger
from utils.normalization import normalize_text

logger = get_logger(__name__)


def get_medication_by_name(
    name: str, 
    lang: Literal["en", "he"] = "en"
) -> dict:
    """
    Get detailed information about a medication by name.
    
    Args:
        name: Medication name in English or Hebrew
        lang: Preferred language for response ("en" or "he")
        
    Returns:
        Medication details including dosage, usage instructions, prescription requirement
    """
    logger.info("tool_get_medication_by_name", name=name, lang=lang)
    
    if not name or not name.strip():
        return tool_error(ToolErrorCode.INVALID_INPUT, "Medication name is required")
    
    medication = medication_repo.find_medication_by_name(name.strip())
    
    if not medication:
        return tool_error(
            ToolErrorCode.NOT_FOUND, 
            f"Medication '{name}' not found in our database"
        )
    
    # Format response based on language preference
    if lang == "he":
        data = {
            "id": medication["id"],
            "name": medication["hebrew_name"],
            "name_en": medication["name"],
            "active_ingredient": medication["active_ingredient_hebrew"],
            "dosage_form": medication["dosage_form"],
            "strength": medication["strength"],
            "usage_instructions": medication["usage_instructions_hebrew"],
            "requires_prescription": bool(medication["requires_prescription"])
        }
    else:
        data = {
            "id": medication["id"],
            "name": medication["name"],
            "name_he": medication["hebrew_name"],
            "active_ingredient": medication["active_ingredient"],
            "dosage_form": medication["dosage_form"],
            "strength": medication["strength"],
            "usage_instructions": medication["usage_instructions"],
            "requires_prescription": bool(medication["requires_prescription"])
        }
    
    return tool_success(data)


def check_medication_stock(
    medication_name: str, 
    branch: Optional[str] = None
) -> dict:
    """
    Check stock availability for a medication across branches.
    
    Args:
        medication_name: Medication name to check
        branch: Optional specific branch to check
        
    Returns:
        Stock quantities by branch
    """
    logger.info("tool_check_medication_stock", medication_name=medication_name, branch=branch)
    
    if not medication_name or not medication_name.strip():
        return tool_error(ToolErrorCode.INVALID_INPUT, "Medication name is required")
    
    # First verify medication exists
    medication = medication_repo.find_medication_by_name(medication_name.strip())
    if not medication:
        return tool_error(
            ToolErrorCode.NOT_FOUND, 
            f"Medication '{medication_name}' not found in our database"
        )
    
    # Get stock data (normalize branch name for flexible matching)
    if branch:
        # Normalize branch input (trim whitespace)
        normalized_branch = normalize_text(branch)
        stock_item = stock_repo.get_stock_at_branch(medication["id"], normalized_branch)
        if not stock_item:
            return tool_error(
                ToolErrorCode.NOT_FOUND, 
                f"Branch '{branch}' not found or no stock record for this medication at this branch"
            )
        stock_list = [stock_item]
    else:
        stock_list = stock_repo.get_stock_by_medication_id(medication["id"])
    
    # Format stock data
    branches_data = []
    total_quantity = 0
    
    for stock in stock_list:
        qty = stock["quantity"]
        total_quantity += qty
        branches_data.append({
            "branch": stock["branch"],
            "quantity": qty,
            "available": qty > 0
        })
    
    data = {
        "medication_name": medication["name"],
        "medication_name_he": medication["hebrew_name"],
        "branches": branches_data,
        "total_quantity": total_quantity,
        "any_available": total_quantity > 0
    }
    
    return tool_success(data)


def get_prescription_requirement(medication_name: str) -> dict:
    """
    Check if a medication requires a prescription.
    
    Args:
        medication_name: Medication name to check
        
    Returns:
        Whether the medication requires a prescription
    """
    logger.info("tool_get_prescription_requirement", medication_name=medication_name)
    
    if not medication_name or not medication_name.strip():
        return tool_error(ToolErrorCode.INVALID_INPUT, "Medication name is required")
    
    medication = medication_repo.find_medication_by_name(medication_name.strip())
    
    if not medication:
        return tool_error(
            ToolErrorCode.NOT_FOUND, 
            f"Medication '{medication_name}' not found in our database"
        )
    
    requires_rx = bool(medication["requires_prescription"])
    
    data = {
        "medication_name": medication["name"],
        "medication_name_he": medication["hebrew_name"],
        "requires_prescription": requires_rx,
        "message": (
            f"{medication['name']} requires a valid prescription from a doctor."
            if requires_rx else
            f"{medication['name']} is available over-the-counter without a prescription."
        )
    }
    
    return tool_success(data)

