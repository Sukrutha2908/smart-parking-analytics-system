from fastapi import APIRouter, HTTPException
from pymongo.errors import PyMongoError

from app.models.vehicle_model import VehicleModel
from app.mongodb import vehicle_collection

router = APIRouter(
    prefix="/vehicle",
    tags=["Vehicle"]
)


# Add Vehicle
@router.post("/")
def add_vehicle(vehicle: VehicleModel):

    try:
        vehicle_dict = vehicle.model_dump()

        # Insert into MongoDB
        result = vehicle_collection.insert_one(vehicle_dict)

        return {
            "message": "Vehicle Added Successfully",
            "inserted_id": str(result.inserted_id),
            "data": vehicle_dict
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


# Get All Vehicles
@router.get("/")
def get_vehicles():

    try:
        vehicles = list(
            vehicle_collection.find({}, {"_id": 0})
        )

        if not vehicles:
            raise HTTPException(
                status_code=404,
                detail="No Vehicles Found"
            )

        return {
            "count": len(vehicles),
            "data": vehicles
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


# Get Vehicle By ID
@router.get("/{vehicle_id}")
def get_vehicle(vehicle_id: int):

    try:
        vehicle = vehicle_collection.find_one(
            {"vehicle_id": vehicle_id},
            {"_id": 0}
        )

        if not vehicle:
            raise HTTPException(
                status_code=404,
                detail=f"No Vehicle Found for ID {vehicle_id}"
            )

        return {
            "data": vehicle
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