from pydantic import BaseModel

class SlotModel(BaseModel):
    floor: str
    slot_number: int
    slot_id: str
    status: str