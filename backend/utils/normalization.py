"""
Input normalization utilities for flexible matching.
Handles phone numbers, branch names, emails, and general text.
"""
import re


def normalize_phone(phone: str) -> str:
    """
    Normalize phone number by removing all non-digit characters.
    
    Examples:
        "054-7890123" -> "0547890123"
        "054 789 0123" -> "0547890123"
        "(054) 789-0123" -> "0547890123"
        "0547890123" -> "0547890123"
    
    Args:
        phone: Phone number string in any format
        
    Returns:
        Phone number with only digits
    """
    if not phone:
        return ""
    return re.sub(r'\D', '', phone)


def normalize_branch(branch: str) -> str:
    """
    Normalize branch name for flexible matching.
    Converts to lowercase and removes spaces, hyphens, and underscores.
    
    Examples:
        "Main Street" -> "mainstreet"
        "main-street" -> "mainstreet"
        "MainStreet" -> "mainstreet"
        "MAIN STREET" -> "mainstreet"
    
    Args:
        branch: Branch name in any format
        
    Returns:
        Normalized branch name (lowercase, no spaces/hyphens)
    """
    if not branch:
        return ""
    # Lowercase and remove spaces, hyphens, underscores
    normalized = branch.lower()
    normalized = re.sub(r'[\s\-_]+', '', normalized)
    return normalized


def normalize_email(email: str) -> str:
    """
    Normalize email address for matching.
    Converts to lowercase and strips whitespace.
    
    Examples:
        "User@Email.COM" -> "user@email.com"
        "  user@email.com  " -> "user@email.com"
        "USER@EMAIL.COM" -> "user@email.com"
    
    Args:
        email: Email address string
        
    Returns:
        Normalized email (lowercase, trimmed)
    """
    if not email:
        return ""
    return email.strip().lower()


def normalize_text(text: str) -> str:
    """
    General text normalization.
    Trims whitespace and normalizes internal spaces to single space.
    
    Examples:
        "  Hello   World  " -> "Hello World"
        "Multiple   Spaces" -> "Multiple Spaces"
    
    Args:
        text: Text string to normalize
        
    Returns:
        Normalized text (trimmed, single spaces)
    """
    if not text:
        return ""
    # Strip leading/trailing whitespace and collapse multiple spaces
    return re.sub(r'\s+', ' ', text.strip())

