from fastapi import APIRouter, HTTPException

import pymongo
from pymongo.errors import PyMongoError

from app.mongodb import (
    slot_collection,
    parking_collection,
    billing_collection,
    transaction_collection,
    parking_collection,
    vehicle_collection
)

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)

# =========================================================
# Parking Occupancy Analytics
# =========================================================

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


# =========================================================
# Revenue Analytics
# =========================================================

@router.get("/revenue")
def revenue():

    try:

        pipeline = [

            {
                "$group": {

                    "_id": {
                        "$dayOfWeek": {
                            "date": "$billing_time",
                            "timezone": "Asia/Kolkata"
                        }
                    },

                    "total_revenue": {
                        "$sum": "$amount"
                    }
                }
            }
        ]

        result = list(
            billing_collection.aggregate(pipeline)
        )

        day_map = {

            1: "Sun",
            2: "Mon",
            3: "Tue",
            4: "Wed",
            5: "Thu",
            6: "Fri",
            7: "Sat"
        }

        weekly_data = {

            "Mon": 0,
            "Tue": 0,
            "Wed": 0,
            "Thu": 0,
            "Fri": 0,
            "Sat": 0,
            "Sun": 0
        }

        for item in result:

            day = day_map.get(item["_id"])

            if day:

                weekly_data[day] = item["total_revenue"]

        revenue_data = []

        for day in [

            "Mon",
            "Tue",
            "Wed",
            "Thu",
            "Fri",
            "Sat",
            "Sun"
        ]:

            revenue_data.append({

                "day": day,

                "revenue": weekly_data[day]
            })

        return revenue_data

    except Exception as e:

        return {
            "error": str(e)
        }


# =========================================================
# Peak Hours Analytics
# =========================================================

@router.get("/peak-hours")
def peak_hours():

    try:

        pipeline = [

            {
                "$group": {

                    "_id": "$entry_hour",

                    "count": {
                        "$sum": 1
                    }
                }
            },

            {
                "$sort": {
                    "count": -1
                }
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


# =========================================================
# Vehicle Count Analytics
# =========================================================

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
            detail=str(e)
        )