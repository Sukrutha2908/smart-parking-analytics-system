from fastapi import APIRouter, HTTPException
from pymongo.errors import PyMongoError

from app.models.parking_model import ParkingModel
from app.mongodb import parking_collection

router = APIRouter(
    prefix="/parking",
    tags=["Parking"]
)

# Create Parking Entry

@router.post("/")
def create_parking(parking: ParkingModel):

    try:

        parking_dict = parking.dict()

        result = parking_collection.insert_one(parking_dict)

        return {
            "message": "Parking Record Created",
            "inserted_id": str(result.inserted_id),
            "data": parking_dict
        }

    except HTTPException as e:
        raise e

    except PyMongoError as e:

        raise HTTPException(
            status_code=500,
            detail=f"Database Error: {str(e)}"
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Unexpected Error: {str(e)}"
        )

# Get All Parking Records

@router.get("/")
def get_parking_records():

    try:

        records = list(
            parking_collection.find({}, {"_id": 0})
        )

        if not records:

            raise HTTPException(
                status_code=404,
                detail="No Parking Records Found"
            )

        return {
            "count": len(records),
            "data": records
        }

    except HTTPException as e:
        raise e

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Unexpected Error: {str(e)}"
        )

# Get Parking By Vehicle ID

@router.get("/{vehicle_id}")
def get_parking_by_vehicle(vehicle_id: int):

    try:

        record = parking_collection.find_one(
            {"vehicle_id": vehicle_id},
            {"_id": 0}
        )

        if not record:

            raise HTTPException(
                status_code=404,
                detail=f"No Record Found for Vehicle ID {vehicle_id}"
            )

        return {
            "data": record
        }

    except HTTPException as e:
        raise e

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Unexpected Error: {str(e)}"
        )