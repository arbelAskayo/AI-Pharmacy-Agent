"""
SQLite database connection and initialization.
Uses raw SQL for simplicity.
"""
import sqlite3
from contextlib import contextmanager
from typing import Generator
from pathlib import Path

from config import settings
from logging_config import get_logger

logger = get_logger(__name__)

# Extract database file path from URL
# Format: sqlite:///./pharmacy.db -> ./pharmacy.db
DB_PATH = settings.database_url.replace("sqlite:///", "")


def get_db_path() -> Path:
    """Get the database file path."""
    return Path(DB_PATH)


def create_connection() -> sqlite3.Connection:
    """Create a new database connection."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    return conn


@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Context manager for database connections."""
    conn = create_connection()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error("database_error", error=str(e))
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Initialize database schema - create tables if they don't exist."""
    logger.info("database_init_start")
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                hebrew_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT NOT NULL
            )
        """)
        
        # Medications table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS medications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                hebrew_name TEXT NOT NULL,
                active_ingredient TEXT NOT NULL,
                active_ingredient_hebrew TEXT NOT NULL,
                dosage_form TEXT NOT NULL,
                strength TEXT NOT NULL,
                usage_instructions TEXT NOT NULL,
                usage_instructions_hebrew TEXT NOT NULL,
                requires_prescription INTEGER NOT NULL DEFAULT 0
            )
        """)
        
        # Prescriptions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prescriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                medication_id INTEGER NOT NULL,
                prescribed_date TEXT NOT NULL,
                expiry_date TEXT NOT NULL,
                refills_allowed INTEGER NOT NULL,
                refills_used INTEGER NOT NULL DEFAULT 0,
                prescribing_doctor TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (medication_id) REFERENCES medications(id)
            )
        """)
        
        # Stock table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                medication_id INTEGER NOT NULL,
                branch TEXT NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 0,
                last_updated TEXT NOT NULL,
                FOREIGN KEY (medication_id) REFERENCES medications(id)
            )
        """)
        
        # Refill requests table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS refill_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                prescription_id INTEGER NOT NULL,
                request_date TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (prescription_id) REFERENCES prescriptions(id)
            )
        """)
        
        conn.commit()
    
    logger.info("database_init_complete")


def is_db_initialized() -> bool:
    """Check if the database has been initialized with tables."""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='users'
            """)
            return cursor.fetchone() is not None
    except Exception:
        return False


def is_db_seeded() -> bool:
    """Check if the database has been seeded with data."""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            count = cursor.fetchone()[0]
            return count > 0
    except Exception:
        return False

