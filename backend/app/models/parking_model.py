from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ParkingModel(BaseModel):

    vehicle_id: int
    vehicle_type: str
    vehicle_number: str

    slot_id: int
    slot_number: int

    status: str

    vehicle_entry_time: datetime
    vehicle_exit_time: Optional[datetime] = None

    billing_amount: float

    payment_status: str
    payment_method: str

    parking_zone: str

    duration_minutes: int

    peak_hour: bool