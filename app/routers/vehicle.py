from fastapi import APIRouter, HTTPException

from app.models.vehicle_model import VehicleModel

router = APIRouter(
    prefix="/vehicle",
    tags=["Vehicle"]
)

@router.post("/")
def add_vehicle(vehicle: VehicleModel):

    try:

        vehicle_dict = vehicle.dict()

        return {
            "message": "Vehicle Added Successfully",
            "data": vehicle_dict
        }

    except HTTPException as e:
        raise e

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/")
def get_vehicles():

    try:

        vehicles = []

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

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )