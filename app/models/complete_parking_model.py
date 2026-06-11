from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CompleteParkingModel(BaseModel):
    # Vehicle Details
    vehicle_id: int
    vehicle_number: str
    vehicle_type: str
    owner_name: str
    owner_phone: str
    
    # Slot Details
    slot_id: int
    slot_number: int
    parking_zone: str
    slot_type: str
    # Parking Details
    status: str
    vehicle_entry_time: datetime
    vehicle_exit_time: Optional[datetime] = None
    duration_minutes: int
    peak_hour: bool
    # Billing Details
    billing_amount: float
    tax_amount: float
    total_amount: float
    # Payment Details
    payment_status: str
    payment_method: str
    # Transaction Details
    transaction_id: int
    transaction_time: datetime