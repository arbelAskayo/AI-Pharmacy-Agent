"""
Unit tests for user-related tools.
Tests user lookup with various phone number and email formats.
"""
import pytest
from tools.user_tools import get_user_profile


class TestGetUserProfile:
    """Tests for the get_user_profile tool."""
    
    def test_user_by_id(self):
        """Should find user by ID."""
        result = get_user_profile(user_id=1)
        
        assert result["success"] is True
        data = result["data"]
        assert data["id"] == 1
        assert data["name"] == "David Cohen"
        assert data["name_he"] == "דוד כהן"
    
    def test_user_by_phone_with_hyphens(self):
        """Should find user with phone number containing hyphens."""
        # User 1 has phone: "050-1234567"
        result = get_user_profile(phone="050-1234567")
        
        assert result["success"] is True
        assert result["data"]["name"] == "David Cohen"
    
    def test_user_by_phone_without_hyphens(self):
        """Should find user with phone number without formatting."""
        # User 1 has phone stored as: "050-1234567"
        # Should still find with: "0501234567"
        result = get_user_profile(phone="0501234567")
        
        assert result["success"] is True
        assert result["data"]["name"] == "David Cohen"
    
    def test_user_by_phone_with_spaces(self):
        """Should find user with phone number containing spaces."""
        # User 1 has phone: "050-1234567"
        result = get_user_profile(phone="050 123 4567")
        
        assert result["success"] is True
        assert result["data"]["name"] == "David Cohen"
    
    def test_user_by_phone_variations(self):
        """Should find user regardless of phone formatting."""
        # Test various formats for the same phone number
        formats = [
            "050-1234567",
            "0501234567",
            "050 123 4567",
            "050-123-4567",
            "(050) 123-4567"
        ]
        
        for phone_format in formats:
            result = get_user_profile(phone=phone_format)
            assert result["success"] is True, f"Failed for format: {phone_format}"
            assert result["data"]["name"] == "David Cohen"
    
    def test_user_by_email(self):
        """Should find user by email."""
        result = get_user_profile(email="david.cohen@email.com")
        
        assert result["success"] is True
        assert result["data"]["name"] == "David Cohen"
    
    def test_user_by_email_case_insensitive(self):
        """Should find user by email regardless of case."""
        result1 = get_user_profile(email="david.cohen@email.com")
        result2 = get_user_profile(email="DAVID.COHEN@EMAIL.COM")
        result3 = get_user_profile(email="David.Cohen@Email.Com")
        
        assert result1["success"] is True
        assert result2["success"] is True
        assert result3["success"] is True
        
        assert result1["data"]["id"] == result2["data"]["id"] == result3["data"]["id"]
    
    def test_user_by_email_with_whitespace(self):
        """Should find user by email even with extra whitespace."""
        result = get_user_profile(email="  david.cohen@email.com  ")
        
        assert result["success"] is True
        assert result["data"]["name"] == "David Cohen"
    
    def test_user_not_found_by_phone(self):
        """Should return NOT_FOUND error for non-existent phone."""
        result = get_user_profile(phone="999-9999999")
        
        assert result["success"] is False
        assert result["error"]["code"] == "NOT_FOUND"
    
    def test_user_not_found_by_email(self):
        """Should return NOT_FOUND error for non-existent email."""
        result = get_user_profile(email="nonexistent@email.com")
        
        assert result["success"] is False
        assert result["error"]["code"] == "NOT_FOUND"
    
    def test_user_not_found_by_id(self):
        """Should return NOT_FOUND error for non-existent ID."""
        result = get_user_profile(user_id=999)
        
        assert result["success"] is False
        assert result["error"]["code"] == "NOT_FOUND"
    
    def test_no_identifier_provided(self):
        """Should return INVALID_INPUT when no identifier provided."""
        result = get_user_profile()
        
        assert result["success"] is False
        assert result["error"]["code"] == "INVALID_INPUT"
    
    def test_response_structure(self):
        """Should have correct response structure."""
        result = get_user_profile(user_id=1)
        
        assert result["success"] is True
        data = result["data"]
        
        assert "id" in data
        assert "name" in data
        assert "name_he" in data
        assert "phone" in data
        assert "email" in data

