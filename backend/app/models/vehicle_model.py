from pydantic import BaseModel

class VehicleModel(BaseModel):
    vehicle_id: int
    vehicle_number: str
    vehicle_type: str
    owner_name: str
    owner_phone: str
