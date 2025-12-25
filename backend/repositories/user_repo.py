"""
User repository - database access for users table.
"""
from typing import Optional
from database import get_db
from logging_config import get_logger
from utils.normalization import normalize_phone, normalize_email

logger = get_logger(__name__)


def get_user_by_id(user_id: int) -> Optional[dict]:
    """Get a user by their ID."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


def find_user_by_search_term(search_term: str) -> Optional[dict]:
    """
    Find a user by phone, email, or name (English or Hebrew).
    Returns the first matching user.
    Normalizes phone and email for flexible matching.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Try exact phone match with normalization (most common use case)
        normalized_phone = normalize_phone(search_term)
        if normalized_phone:
            cursor.execute(
                """SELECT * FROM users 
                   WHERE REPLACE(REPLACE(REPLACE(phone, '-', ''), ' ', ''), '(', '') 
                   LIKE ?
                   LIMIT 1""",
                (f"%{normalized_phone}%",)
            )
            row = cursor.fetchone()
            if row:
                logger.info("user_found_by_phone", search_term=search_term, user_id=row["id"])
                return dict(row)
        
        # Try email match with normalization
        normalized_email = normalize_email(search_term)
        if normalized_email and '@' in normalized_email:
            cursor.execute(
                """SELECT * FROM users 
                   WHERE LOWER(email) = ?
                   LIMIT 1""",
                (normalized_email,)
            )
            row = cursor.fetchone()
            if row:
                logger.info("user_found_by_email", search_term=search_term, user_id=row["id"])
                return dict(row)
        
        # Fallback: Try name search (English or Hebrew)
        search_pattern = f"%{search_term}%"
        cursor.execute(
            """SELECT * FROM users 
               WHERE name LIKE ? 
               OR hebrew_name LIKE ?
               LIMIT 1""",
            (search_pattern, search_pattern)
        )
        row = cursor.fetchone()
        if row:
            logger.info("user_found_by_name", search_term=search_term, user_id=row["id"])
            return dict(row)
        
        logger.info("user_not_found", search_term=search_term)
        return None


def get_all_users() -> list[dict]:
    """Get all users (for debugging)."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users ORDER BY id")
        return [dict(row) for row in cursor.fetchall()]

