"""
Data Transfer Objects (DTOs) for API responses.
"""
from pydantic import BaseModel
from typing import Optional, List


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    database: str
    openai: str
    llm_enabled: bool = False
    evaluation_doc: str = "docs/evaluation_plan.md"


class UserDTO(BaseModel):
    """User data transfer object."""
    id: int
    name: str
    hebrew_name: str
    phone: str
    email: str


class MedicationDTO(BaseModel):
    """Medication data transfer object."""
    id: int
    name: str
    hebrew_name: str
    active_ingredient: str
    active_ingredient_hebrew: str
    dosage_form: str
    strength: str
    usage_instructions: str
    usage_instructions_hebrew: str
    requires_prescription: bool


class MedicationListResponse(BaseModel):
    """Response for listing medications."""
    medications: List[MedicationDTO]


class StockDTO(BaseModel):
    """Stock information for a medication at a branch."""
    branch: str
    quantity: int
    available: bool


class PrescriptionDTO(BaseModel):
    """Prescription data transfer object."""
    id: int
    medication_name: str
    medication_hebrew_name: str
    prescribed_date: str
    expiry_date: str
    refills_allowed: int
    refills_used: int
    refills_remaining: int
    prescribing_doctor: str

