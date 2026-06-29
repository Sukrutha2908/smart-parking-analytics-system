from fastapi import APIRouter, HTTPException
from pymongo.errors import PyMongoError

from app.mongodb import slot_collection

from app.mongodb import (
    parking_collection,
    billing_collection,
    transaction_collection,
    vehicle_collection
)

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)

# Parking Occupancy
@router.get("/occupancy")
def parking_occupancy():

    try:
        total_slots = parking_collection.count_documents({})

        occupied_slots = parking_collection.count_documents(
            {"status": "Occupied"}
        )

        if total_slots == 0:
            raise HTTPException(
                status_code=404,
                detail="No Parking Slot Data Found"
            )

        occupancy_rate = (
            occupied_slots / total_slots
        ) * 100

        return {
            "total_slots": total_slots,
            "occupied_slots": occupied_slots,
            "occupancy_rate": f"{occupancy_rate:.2f}%"
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


# Revenue Analytics
from datetime import datetime

@router.get("/revenue")
def revenue():

    try:

        pipeline = [

            {
                "$group": {

                    "_id": {
                        "$dateToString": {
                            "format": "%H:%M",
                            "date": "$billing_time"
                        }
                    },

                    "total_revenue": {
                        "$sum": "$amount"
                    }
                }
            },

            {
                "$sort": {
                    "_id": 1
                }
            }
        ]

        result = list(
            billing_collection.aggregate(pipeline)
        )

        revenue_data = []

        for item in result:

            revenue_data.append({

                "date": item["_id"],

                "revenue": item["total_revenue"]
            })

        return revenue_data

    except Exception as e:

        return {
            "error": str(e)
        }
    
# Peak Hour Analytics
@router.get("/peak-hours")
def peak_hours():

    try:
        pipeline = [
            {
                "$group": {
                    "_id": "$entry_hour",
                    "count": {"$sum": 1}
                }
            },
            {
                "$sort": {"count": -1}
            },
            {
                "$limit": 1
            }
        ]

        result = list(
            parking_collection.aggregate(pipeline)
        )

        if not result:
            raise HTTPException(
                status_code=404,
                detail="No Peak Hour Data Found"
            )

        return {
            "peak_hour": result[0]["_id"],
            "vehicle_count": result[0]["count"]
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


# Vehicle Count Analytics
@router.get("/vehicle-count")
def vehicle_count():

    try:
        total_vehicles = vehicle_collection.count_documents({})

        return {
            "total_vehicles": total_vehicles
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

@router.get("/vehicle-distribution")
async def vehicle_distribution():

    total = slot_collection.count_documents(
        {"status": "occupied"}
    )

    cars = slot_collection.count_documents(
        {
            "status": "occupied",
            "vehicle_type": "Car"
        }
    )

    bikes = slot_collection.count_documents(
        {
            "status": "occupied",
            "vehicle_type": "Bike"
        }
    )

    trucks = slot_collection.count_documents(
        {
            "status": "occupied",
            "vehicle_type": "Truck"
        }
    )

    return {
        "cars": cars,
        "bikes": bikes,
        "trucks": trucks,
        "total": total
    }