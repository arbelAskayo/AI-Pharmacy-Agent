"""
Unit tests for input normalization utilities.
Tests phone, email, branch, and text normalization functions.
"""
import pytest
from utils.normalization import (
    normalize_phone,
    normalize_branch,
    normalize_email,
    normalize_text
)


class TestNormalizePhone:
    """Tests for phone number normalization."""
    
    def test_phone_with_hyphens(self):
        """Should remove hyphens from phone number."""
        assert normalize_phone("054-7890123") == "0547890123"
        assert normalize_phone("050-123-4567") == "0501234567"
    
    def test_phone_with_spaces(self):
        """Should remove spaces from phone number."""
        assert normalize_phone("054 789 0123") == "0547890123"
        assert normalize_phone("050 1234567") == "0501234567"
    
    def test_phone_with_parentheses(self):
        """Should remove parentheses and other formatting."""
        assert normalize_phone("(054) 789-0123") == "0547890123"
        assert normalize_phone("(050)-123-4567") == "0501234567"
    
    def test_phone_already_normalized(self):
        """Should handle already normalized phone numbers."""
        assert normalize_phone("0547890123") == "0547890123"
        assert normalize_phone("0501234567") == "0501234567"
    
    def test_phone_with_plus_sign(self):
        """Should remove country code plus sign."""
        assert normalize_phone("+972-54-7890123") == "972547890123"
        assert normalize_phone("+1-555-123-4567") == "15551234567"
    
    def test_phone_empty(self):
        """Should handle empty string."""
        assert normalize_phone("") == ""
        assert normalize_phone(None) == ""
    
    def test_phone_mixed_formatting(self):
        """Should handle various mixed formatting."""
        assert normalize_phone("054-789 0123") == "0547890123"
        assert normalize_phone("(054) 789 0123") == "0547890123"
        assert normalize_phone("054.789.0123") == "0547890123"


class TestNormalizeBranch:
    """Tests for branch name normalization."""
    
    def test_branch_with_spaces(self):
        """Should remove spaces from branch name."""
        assert normalize_branch("Main Street") == "mainstreet"
        assert normalize_branch("Down Town") == "downtown"
    
    def test_branch_with_hyphens(self):
        """Should remove hyphens from branch name."""
        assert normalize_branch("main-street") == "mainstreet"
        assert normalize_branch("down-town") == "downtown"
    
    def test_branch_mixed_case(self):
        """Should convert to lowercase."""
        assert normalize_branch("MAIN STREET") == "mainstreet"
        assert normalize_branch("Main Street") == "mainstreet"
        assert normalize_branch("MainStreet") == "mainstreet"
    
    def test_branch_already_normalized(self):
        """Should handle already normalized branch names."""
        assert normalize_branch("mainstreet") == "mainstreet"
        assert normalize_branch("downtown") == "downtown"
        assert normalize_branch("airport") == "airport"
    
    def test_branch_with_underscores(self):
        """Should remove underscores from branch name."""
        assert normalize_branch("main_street") == "mainstreet"
        assert normalize_branch("down_town") == "downtown"
    
    def test_branch_empty(self):
        """Should handle empty string."""
        assert normalize_branch("") == ""
        assert normalize_branch(None) == ""
    
    def test_branch_multiple_spaces(self):
        """Should remove multiple consecutive spaces."""
        assert normalize_branch("Main   Street") == "mainstreet"
        assert normalize_branch("  Main Street  ") == "mainstreet"


class TestNormalizeEmail:
    """Tests for email normalization."""
    
    def test_email_uppercase(self):
        """Should convert email to lowercase."""
        assert normalize_email("USER@EMAIL.COM") == "user@email.com"
        assert normalize_email("User@Email.Com") == "user@email.com"
    
    def test_email_with_whitespace(self):
        """Should trim whitespace from email."""
        assert normalize_email("  user@email.com  ") == "user@email.com"
        assert normalize_email("user@email.com ") == "user@email.com"
        assert normalize_email(" user@email.com") == "user@email.com"
    
    def test_email_already_normalized(self):
        """Should handle already normalized emails."""
        assert normalize_email("user@email.com") == "user@email.com"
        assert normalize_email("test@example.org") == "test@example.org"
    
    def test_email_empty(self):
        """Should handle empty string."""
        assert normalize_email("") == ""
        assert normalize_email(None) == ""
    
    def test_email_mixed_case_and_whitespace(self):
        """Should handle both case and whitespace together."""
        assert normalize_email("  User@Email.COM  ") == "user@email.com"


class TestNormalizeText:
    """Tests for general text normalization."""
    
    def test_text_trim_whitespace(self):
        """Should trim leading and trailing whitespace."""
        assert normalize_text("  Hello World  ") == "Hello World"
        assert normalize_text("Test") == "Test"
    
    def test_text_collapse_spaces(self):
        """Should collapse multiple spaces to single space."""
        assert normalize_text("Hello   World") == "Hello World"
        assert normalize_text("Multiple   Spaces   Here") == "Multiple Spaces Here"
    
    def test_text_mixed_whitespace(self):
        """Should handle tabs and newlines."""
        assert normalize_text("Hello\t\tWorld") == "Hello World"
        assert normalize_text("Hello\n\nWorld") == "Hello World"
    
    def test_text_already_normalized(self):
        """Should handle already normalized text."""
        assert normalize_text("Hello World") == "Hello World"
        assert normalize_text("Test") == "Test"
    
    def test_text_empty(self):
        """Should handle empty string."""
        assert normalize_text("") == ""
        assert normalize_text(None) == ""
    
    def test_text_preserve_case(self):
        """Should preserve original case."""
        assert normalize_text("  Hello WORLD  ") == "Hello WORLD"
        assert normalize_text("MixedCase Text") == "MixedCase Text"

