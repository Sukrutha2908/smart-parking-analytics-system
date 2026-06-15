from fastapi import APIRouter, HTTPException

from app.models.slot_model import SlotModel

router = APIRouter(
    prefix="/slots",
    tags=["Slots"]
)

@router.post("/")
def create_slot(slot: SlotModel):

    try:

        slot_dict = slot.dict()

        return {
            "message": "Slot Created Successfully",
            "data": slot_dict
        }

    except HTTPException as e:
        raise e

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/")
def get_slots():

    try:

        slots = list(
            slots_collection.find(
                {},
                {"_id": 0}
            )
        )

        return slots

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )