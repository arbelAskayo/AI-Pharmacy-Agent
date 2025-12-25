"""
User repository - database access for users table.
"""
from typing import Optional
from database import get_db
from logging_config import get_logger

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
    """
    search_pattern = f"%{search_term}%"
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT * FROM users 
               WHERE phone LIKE ? 
               OR email LIKE ? 
               OR name LIKE ? 
               OR hebrew_name LIKE ?
               LIMIT 1""",
            (search_pattern, search_pattern, search_pattern, search_pattern)
        )
        row = cursor.fetchone()
        if row:
            logger.info("user_found", search_term=search_term, user_id=row["id"])
            return dict(row)
        logger.info("user_not_found", search_term=search_term)
        return None


def get_all_users() -> list[dict]:
    """Get all users (for debugging)."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users ORDER BY id")
        return [dict(row) for row in cursor.fetchall()]

