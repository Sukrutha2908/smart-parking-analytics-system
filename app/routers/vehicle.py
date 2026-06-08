from fastapi import APIRouter

from app.models.vehicle_model import VehicleModel

router = APIRouter(
prefix="/vehicle",
tags=["Vehicle"]
)

# Add Vehicle

@router.post("/")
def add_vehicle(vehicle: VehicleModel):

    return {
        "message": "Vehicle Added Successfully",
        "data": vehicle
    }

# Get Vehicles

@router.get("/")
def get_vehicles():
    return {
    "message": "All Vehicles"
}