from pydantic import BaseModel

class BillingModel(BaseModel):
    billing_id: int
    vehicle_id: int
    amount: float
    tax: float
    total_amount: float
    payment_status: str