from fastapi import APIRouter, HTTPException
from pymongo.errors import PyMongoError

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
@router.get("/revenue")
def revenue():

    try:
        transactions = list(
            transaction_collection.find({}, {"_id": 0})
        )

        if not transactions:
            raise HTTPException(
                status_code=404,
                detail="No Transaction Data Found"
            )

        total_revenue = sum(
            transaction.get("amount", 0)
            for transaction in transactions
        )

        return {
            "total_revenue": total_revenue
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