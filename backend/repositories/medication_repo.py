"""
Medication repository - database access for medications table.
"""
from typing import Optional
from database import get_db
from logging_config import get_logger

logger = get_logger(__name__)


def get_medication_by_id(medication_id: int) -> Optional[dict]:
    """Get a medication by its ID."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM medications WHERE id = ?", (medication_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


def find_medication_by_name(name: str) -> Optional[dict]:
    """
    Find a medication by name (English or Hebrew).
    Case-insensitive search.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        # Try exact match first (case-insensitive)
        cursor.execute(
            """SELECT * FROM medications 
               WHERE LOWER(name) = LOWER(?) 
               OR LOWER(hebrew_name) = LOWER(?)
               LIMIT 1""",
            (name, name)
        )
        row = cursor.fetchone()
        
        if not row:
            # Try partial match
            search_pattern = f"%{name}%"
            cursor.execute(
                """SELECT * FROM medications 
                   WHERE name LIKE ? OR hebrew_name LIKE ?
                   LIMIT 1""",
                (search_pattern, search_pattern)
            )
            row = cursor.fetchone()
        
        if row:
            logger.info("medication_found", search_name=name, medication_id=row["id"])
            return dict(row)
        
        logger.info("medication_not_found", search_name=name)
        return None


def get_all_medications() -> list[dict]:
    """Get all medications."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM medications ORDER BY name")
        return [dict(row) for row in cursor.fetchall()]

