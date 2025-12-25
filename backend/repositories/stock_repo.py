"""
Stock repository - database access for stock table.
"""
from typing import Optional
from datetime import datetime
from database import get_db
from logging_config import get_logger

logger = get_logger(__name__)


def get_stock_by_medication_id(medication_id: int) -> list[dict]:
    """Get stock levels for a medication across all branches."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT s.*, m.name as medication_name 
               FROM stock s
               JOIN medications m ON s.medication_id = m.id
               WHERE s.medication_id = ?
               ORDER BY s.branch""",
            (medication_id,)
        )
        return [dict(row) for row in cursor.fetchall()]


def get_stock_by_medication_name(medication_name: str) -> list[dict]:
    """Get stock levels for a medication by name (English or Hebrew)."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT s.*, m.name as medication_name, m.hebrew_name as medication_hebrew_name
               FROM stock s
               JOIN medications m ON s.medication_id = m.id
               WHERE LOWER(m.name) = LOWER(?) 
               OR LOWER(m.hebrew_name) = LOWER(?)
               OR m.name LIKE ? 
               OR m.hebrew_name LIKE ?
               ORDER BY s.branch""",
            (medication_name, medication_name, f"%{medication_name}%", f"%{medication_name}%")
        )
        results = [dict(row) for row in cursor.fetchall()]
        logger.info("stock_query", medication_name=medication_name, branches_found=len(results))
        return results


def get_stock_at_branch(medication_id: int, branch: str) -> Optional[dict]:
    """Get stock for a specific medication at a specific branch."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT s.*, m.name as medication_name
               FROM stock s
               JOIN medications m ON s.medication_id = m.id
               WHERE s.medication_id = ? AND LOWER(s.branch) = LOWER(?)""",
            (medication_id, branch)
        )
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


def update_stock_quantity(medication_id: int, branch: str, quantity_change: int) -> bool:
    """
    Update stock quantity at a branch.
    quantity_change can be negative (for reservations) or positive (for restocking).
    Returns True if successful, False if insufficient stock.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Get current stock
        cursor.execute(
            "SELECT quantity FROM stock WHERE medication_id = ? AND LOWER(branch) = LOWER(?)",
            (medication_id, branch)
        )
        row = cursor.fetchone()
        
        if not row:
            logger.warning("stock_not_found", medication_id=medication_id, branch=branch)
            return False
        
        new_quantity = row["quantity"] + quantity_change
        
        if new_quantity < 0:
            logger.warning("insufficient_stock", 
                          medication_id=medication_id, 
                          branch=branch, 
                          current=row["quantity"],
                          requested=-quantity_change)
            return False
        
        cursor.execute(
            """UPDATE stock SET quantity = ?, last_updated = ?
               WHERE medication_id = ? AND LOWER(branch) = LOWER(?)""",
            (new_quantity, datetime.now().isoformat(), medication_id, branch)
        )
        conn.commit()
        
        logger.info("stock_updated", 
                   medication_id=medication_id, 
                   branch=branch, 
                   old_quantity=row["quantity"],
                   new_quantity=new_quantity)
        return True


def get_all_branches() -> list[str]:
    """Get list of all branches."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT branch FROM stock ORDER BY branch")
        return [row["branch"] for row in cursor.fetchall()]

