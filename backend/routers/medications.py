"""
Medications debug endpoint.
For development/debugging only - lists all medications in the database.
"""
from fastapi import APIRouter

from repositories import medication_repo
from schemas.dto import MedicationDTO, MedicationListResponse

router = APIRouter(prefix="/api", tags=["debug"])


@router.get("/medications", response_model=MedicationListResponse)
async def list_medications() -> MedicationListResponse:
    """
    List all medications in the database.
    This is a debug endpoint for testing the seed data.
    """
    medications = medication_repo.get_all_medications()
    
    # Convert to DTOs
    medication_dtos = [
        MedicationDTO(
            id=m["id"],
            name=m["name"],
            hebrew_name=m["hebrew_name"],
            active_ingredient=m["active_ingredient"],
            active_ingredient_hebrew=m["active_ingredient_hebrew"],
            dosage_form=m["dosage_form"],
            strength=m["strength"],
            usage_instructions=m["usage_instructions"],
            usage_instructions_hebrew=m["usage_instructions_hebrew"],
            requires_prescription=bool(m["requires_prescription"]),
        )
        for m in medications
    ]
    
    return MedicationListResponse(medications=medication_dtos)

