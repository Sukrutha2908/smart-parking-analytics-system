from pydantic import BaseModel

class SlotModel(BaseModel):
    slot_id: int
    slot_number: int
    slot_type: str
    floor_number: int
    parking_zone: str
    is_available: bool
