from fastapi import APIRouter
from app.mongodb import parking_collection
from app.models.parking_model import ParkingModel

router = APIRouter()

# Add parking data
@router.post("/add-parking")
async def add_parking(data: ParkingModel):

    parking_data = data.dict()

    result = await parking_collection.insert_one(parking_data)

    return {
        "message": "Parking data inserted successfully",
        "id": str(result.inserted_id)
    }

# Get all parking records
@router.get("/all-parking")
async def get_all_parking():

    data = []

    async for document in parking_collection.find():

        document["_id"] = str(document["_id"])

        data.append(document)

    return data