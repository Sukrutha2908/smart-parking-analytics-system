# app/models/parking_model.py

from pydantic import BaseModel

class ParkingModel(BaseModel):
    vehicle_id: str
    vehicle_number: str
    vehicle_type: str
    slot_id: str
    slot_number: int
    status: str
    entry_time: str
    exit_time: str
    duration_minutes: int
    billing_amount: float
    payment_status: str
    payment_method: str
    parking_zone: str