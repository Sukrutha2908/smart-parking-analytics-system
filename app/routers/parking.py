from fastapi import APIRouter

from app.models.parking_model import ParkingModel

from app.mongodb import parking_collection

router = APIRouter(
prefix="/parking",
tags=["Parking"]
)

# Create Parking Entry

@router.post("/")
def create_parking(parking: ParkingModel):
    parking_dict = parking.dict()
    result = parking_collection.insert_one(parking_dict)
    return {
    "message": "Parking Record Created",
    "inserted_id": str(result.inserted_id),
    "data": parking
}

# Get All Parking Records

@router.get("/")
def get_parking_records():
    records = list(
    parking_collection.find({}, {"_id": 0})
    )
    return {
    "data": records
}

# Get Parking By Vehicle ID

@router.get("/{vehicle_id}")
def get_parking_by_vehicle(vehicle_id: int):
    record = parking_collection.find_one(
    {"vehicle_id": vehicle_id},
    {"_id": 0}
    )
    return {
    "data": record
}
