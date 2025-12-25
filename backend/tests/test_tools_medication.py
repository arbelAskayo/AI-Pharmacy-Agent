"""
Unit tests for medication-related tools.
Tests the deterministic parts: DB lookups, error handling, response structure.
"""
import pytest
from tools.medication_tools import (
    get_medication_by_name,
    check_medication_stock,
    get_prescription_requirement
)


class TestGetMedicationByName:
    """Tests for the get_medication_by_name tool."""
    
    def test_find_aspirin_english(self):
        """Should find Aspirin and return English response."""
        result = get_medication_by_name("Aspirin", lang="en")
        
        assert result["success"] is True
        assert "data" in result
        
        data = result["data"]
        assert data["name"] == "Aspirin"
        assert data["name_he"] == "אספירין"
        assert data["active_ingredient"] == "Acetylsalicylic acid"
        assert data["requires_prescription"] is False
    
    def test_find_aspirin_hebrew(self):
        """Should find Aspirin and return Hebrew response."""
        result = get_medication_by_name("אספירין", lang="he")
        
        assert result["success"] is True
        data = result["data"]
        assert data["name"] == "אספירין"
        assert data["name_en"] == "Aspirin"
    
    def test_find_prescription_medication(self):
        """Should correctly identify prescription requirement."""
        result = get_medication_by_name("Amoxicillin")
        
        assert result["success"] is True
        assert result["data"]["requires_prescription"] is True
    
    def test_medication_not_found(self):
        """Should return NOT_FOUND error for unknown medications."""
        result = get_medication_by_name("FakeMedication123")
        
        assert result["success"] is False
        assert "error" in result
        assert result["error"]["code"] == "NOT_FOUND"
    
    def test_empty_name_error(self):
        """Should return INVALID_INPUT for empty name."""
        result = get_medication_by_name("")
        
        assert result["success"] is False
        assert result["error"]["code"] == "INVALID_INPUT"
    
    def test_case_insensitive_search(self):
        """Should find medication regardless of case."""
        result1 = get_medication_by_name("ASPIRIN")
        result2 = get_medication_by_name("aspirin")
        result3 = get_medication_by_name("Aspirin")
        
        assert all(r["success"] for r in [result1, result2, result3])
        assert all(r["data"]["name"] == "Aspirin" for r in [result1, result2, result3])


class TestCheckMedicationStock:
    """Tests for the check_medication_stock tool."""
    
    def test_check_aspirin_stock_all_branches(self):
        """Should return stock for all branches."""
        result = check_medication_stock("Aspirin")
        
        assert result["success"] is True
        data = result["data"]
        
        assert data["medication_name"] == "Aspirin"
        assert "branches" in data
        assert len(data["branches"]) > 0
        assert data["total_quantity"] > 0
        assert data["any_available"] is True
    
    def test_check_stock_specific_branch(self):
        """Should return stock for specific branch only."""
        result = check_medication_stock("Aspirin", branch="Main Street")
        
        assert result["success"] is True
        data = result["data"]
        
        assert len(data["branches"]) == 1
        assert data["branches"][0]["branch"] == "Main Street"
    
    def test_stock_medication_not_found(self):
        """Should return error for unknown medication."""
        result = check_medication_stock("FakeMed")
        
        assert result["success"] is False
        assert result["error"]["code"] == "NOT_FOUND"
    
    def test_stock_branch_not_found(self):
        """Should return error for unknown branch."""
        result = check_medication_stock("Aspirin", branch="NonexistentBranch")
        
        assert result["success"] is False
        assert result["error"]["code"] == "NOT_FOUND"
    
    def test_stock_branch_name_variations(self):
        """Should find stock regardless of branch name formatting."""
        # Test various formats of "Main Street"
        result1 = check_medication_stock("Aspirin", branch="Main Street")
        result2 = check_medication_stock("Aspirin", branch="main street")
        result3 = check_medication_stock("Aspirin", branch="MainStreet")
        result4 = check_medication_stock("Aspirin", branch="main-street")
        result5 = check_medication_stock("Aspirin", branch="MAIN STREET")
        
        # All should succeed
        assert result1["success"] is True
        assert result2["success"] is True
        assert result3["success"] is True
        assert result4["success"] is True
        assert result5["success"] is True
        
        # All should return the same branch data
        assert result1["data"]["branches"][0]["branch"] == "Main Street"
        assert result2["data"]["branches"][0]["branch"] == "Main Street"
        assert result3["data"]["branches"][0]["branch"] == "Main Street"
        assert result4["data"]["branches"][0]["branch"] == "Main Street"
        assert result5["data"]["branches"][0]["branch"] == "Main Street"
    
    def test_stock_response_structure(self):
        """Should have correct response structure with Hebrew name."""
        result = check_medication_stock("Ibuprofen")
        
        assert result["success"] is True
        data = result["data"]
        
        assert "medication_name" in data
        assert "medication_name_he" in data
        assert "branches" in data
        assert "total_quantity" in data
        assert "any_available" in data
        
        for branch in data["branches"]:
            assert "branch" in branch
            assert "quantity" in branch
            assert "available" in branch


class TestGetPrescriptionRequirement:
    """Tests for the get_prescription_requirement tool."""
    
    def test_otc_medication(self):
        """Should correctly identify OTC medication."""
        result = get_prescription_requirement("Aspirin")
        
        assert result["success"] is True
        data = result["data"]
        
        assert data["requires_prescription"] is False
        assert "over-the-counter" in data["message"].lower()
    
    def test_prescription_medication(self):
        """Should correctly identify prescription medication."""
        result = get_prescription_requirement("Omeprazole")
        
        assert result["success"] is True
        data = result["data"]
        
        assert data["requires_prescription"] is True
        assert "prescription" in data["message"].lower()
    
    def test_includes_hebrew_name(self):
        """Should include Hebrew name in response."""
        result = get_prescription_requirement("Ibuprofen")
        
        assert result["success"] is True
        assert "medication_name_he" in result["data"]
        assert result["data"]["medication_name_he"] == "איבופרופן"

