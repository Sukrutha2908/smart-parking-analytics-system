from fastapi import APIRouter

from app.models.slot_model import SlotModel

router = APIRouter(
prefix="/slots",
tags=["Slots"]
)

# Create Slot

@router.post("/")
def create_slot(slot: SlotModel):

    return {
        "message": "Slot Created Successfully",
        "data": slot
    }

# Get All Slots

@router.get("/")
def get_slots():
    return {
    "message": "All Parking Slots"
}