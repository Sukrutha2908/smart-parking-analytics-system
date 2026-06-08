from fastapi import APIRouter

router = APIRouter(
prefix="/analytics",
tags=["Analytics"]
)

# Parking Occupancy

@router.get("/occupancy")
def parking_occupancy():
    return {
    "occupancy_rate": "85%"
}

# Revenue Analytics

@router.get("/revenue")
def revenue():
    return {
    "total_revenue": 25000
}

# Peak Hour Analytics

@router.get("/peak-hours")
def peak_hours():
    return {
    "peak_hours": "6 PM - 9 PM"
    }

# Vehicle Count Analytics

@router.get("/vehicle-count")
def vehicle_count():

    return {
        "vehicles_today": 320
    }