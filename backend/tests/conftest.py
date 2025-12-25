"""
Pytest configuration and fixtures for the Pharmacy Assistant tests.
"""
import sys
import os
import pytest

# Add the backend directory to the path so imports work correctly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import init_db
from seed_data import seed_database


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """
    Initialize and seed the database once for all tests.
    This ensures we have consistent test data.
    """
    init_db()
    seed_database()
    yield
    # No teardown needed - we use the same DB file


@pytest.fixture
def sample_medications():
    """Return a list of known medication names for testing."""
    return [
        "Aspirin",
        "Ibuprofen", 
        "Amoxicillin",
        "Omeprazole",
        "Vitamin D3"
    ]


@pytest.fixture
def sample_user_phones():
    """Return a list of known user phone numbers for testing."""
    return [
        "050-1234567",  # David Cohen
        "050-2345678",  # Sarah Levy
        "050-3456789",  # Michael Rosenberg
    ]

