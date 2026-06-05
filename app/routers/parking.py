from fastapi import APIRouter
from app.mongodb import parking_collection
from app.models.parking_model import ParkingModel

router = APIRouter()

@router.post("/parking")
async def add_parking(data: ParkingModel):

    parking_data = data.dict()

    result = await parking_collection.insert_one(parking_data)

    return {
        "message": "Inserted Successfully",
        "id": str(result.inserted_id)
    }