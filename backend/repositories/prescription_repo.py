"""
Prescription repository - database access for prescriptions and refill_requests tables.
"""
from typing import Optional
from datetime import datetime, date
from database import get_db
from logging_config import get_logger

logger = get_logger(__name__)


def get_prescription_by_id(prescription_id: int) -> Optional[dict]:
    """Get a prescription by its ID with medication and user info."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT p.*, 
                      m.name as medication_name, 
                      m.hebrew_name as medication_hebrew_name,
                      u.name as user_name,
                      u.hebrew_name as user_hebrew_name
               FROM prescriptions p
               JOIN medications m ON p.medication_id = m.id
               JOIN users u ON p.user_id = u.id
               WHERE p.id = ?""",
            (prescription_id,)
        )
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


def get_prescriptions_by_user_id(user_id: int, active_only: bool = True) -> list[dict]:
    """
    Get all prescriptions for a user.
    If active_only is True, only returns non-expired prescriptions.
    """
    today = date.today().isoformat()
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        if active_only:
            cursor.execute(
                """SELECT p.*, 
                          m.name as medication_name, 
                          m.hebrew_name as medication_hebrew_name,
                          m.requires_prescription
                   FROM prescriptions p
                   JOIN medications m ON p.medication_id = m.id
                   WHERE p.user_id = ? AND p.expiry_date >= ?
                   ORDER BY p.expiry_date""",
                (user_id, today)
            )
        else:
            cursor.execute(
                """SELECT p.*, 
                          m.name as medication_name, 
                          m.hebrew_name as medication_hebrew_name,
                          m.requires_prescription
                   FROM prescriptions p
                   JOIN medications m ON p.medication_id = m.id
                   WHERE p.user_id = ?
                   ORDER BY p.expiry_date DESC""",
                (user_id,)
            )
        
        results = [dict(row) for row in cursor.fetchall()]
        logger.info("prescriptions_query", user_id=user_id, active_only=active_only, count=len(results))
        return results


def is_prescription_valid(prescription_id: int, user_id: int) -> tuple[bool, str]:
    """
    Check if a prescription is valid for refill.
    Returns (is_valid, reason_if_invalid).
    """
    prescription = get_prescription_by_id(prescription_id)
    
    if not prescription:
        return False, "Prescription not found"
    
    if prescription["user_id"] != user_id:
        return False, "Prescription does not belong to this user"
    
    today = date.today().isoformat()
    if prescription["expiry_date"] < today:
        return False, "Prescription has expired"
    
    refills_remaining = prescription["refills_allowed"] - prescription["refills_used"]
    if refills_remaining <= 0:
        return False, "No refills remaining on this prescription"
    
    return True, ""


def increment_refills_used(prescription_id: int) -> bool:
    """Increment the refills_used count for a prescription."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE prescriptions SET refills_used = refills_used + 1 WHERE id = ?",
            (prescription_id,)
        )
        conn.commit()
        return cursor.rowcount > 0


def create_refill_request(user_id: int, prescription_id: int) -> Optional[int]:
    """
    Create a new refill request.
    Returns the request ID if successful, None otherwise.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO refill_requests (user_id, prescription_id, request_date, status)
               VALUES (?, ?, ?, 'pending')""",
            (user_id, prescription_id, datetime.now().isoformat())
        )
        conn.commit()
        request_id = cursor.lastrowid
        logger.info("refill_request_created", 
                   request_id=request_id, 
                   user_id=user_id, 
                   prescription_id=prescription_id)
        return request_id


def get_refill_requests_by_user(user_id: int) -> list[dict]:
    """Get all refill requests for a user."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT rr.*, 
                      p.medication_id,
                      m.name as medication_name,
                      m.hebrew_name as medication_hebrew_name
               FROM refill_requests rr
               JOIN prescriptions p ON rr.prescription_id = p.id
               JOIN medications m ON p.medication_id = m.id
               WHERE rr.user_id = ?
               ORDER BY rr.request_date DESC""",
            (user_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

