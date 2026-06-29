from pydantic import BaseModel
from typing import Optional

class SlotModel(BaseModel):

    floor: str
    slot_number: int
    slot_id: str
    status: str

    vehicle_number: Optional[str] = None
    vehicle_type: Optional[str] = None
    owner_name: Optional[str] = None

    entry_time: Optional[str] = None
    exit_time: Optional[str] = None

    duration: Optional[str] = None
    amount: Optional[int] = None