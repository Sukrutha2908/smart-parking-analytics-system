from fastapi import APIRouter, HTTPException
from pymongo.errors import PyMongoError

from datetime import datetime, timedelta

from app.mongodb import log_collection

from app.mongodb import (
    slot_collection,
    parking_collection,
    billing_collection,
    transaction_collection,
    vehicle_collection,
    log_collection
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
            detail=f"Unexpected Error: {str(e)}"
        )


# =========================================================
# Vehicle Distribution Analytics
# =========================================================

@router.get("/vehicle-distribution")
def vehicle_distribution():

    logs = list(
        log_collection.find({

        "exit_time": None
        })
    )

    cars = 0
    bikes = 0
    trucks = 0

    for log in logs:

        vehicle_type = log.get(
            "vehicle_type",
            ""
        )

        if vehicle_type == "Four Wheeler":

            cars += 1

        elif vehicle_type == "Two Wheeler":

            bikes += 1

        elif vehicle_type in [
            "Mini Truck",
            "Large Vehicle"
        ]:

            trucks += 1

    total = cars + bikes + trucks

    return {

        "cars": cars,

        "bikes": bikes,

        "trucks": trucks,

        "total": total
    }

# =========================================================
# Weekly Revenue Filter Analytics
# =========================================================


@router.get("/weekly-revenue")
async def weekly_revenue(filter: str = "current"):

    try:

        today = datetime.now()

        # =====================================================
        # MONTHLY ANALYTICS
        # =====================================================

        if filter == "month":

            start_date = today - timedelta(days=30)

            pipeline = [

                {
                    "$match": {

                        "billing_time": {

                            "$gte": start_date,
                            "$lt": today + timedelta(days=1)
                        }
                    }
                },

                {
                    "$group": {

                        "_id": {
                            "$week": "$billing_time"
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

            labels = []
            values = []

            for item in result:

                labels.append(
                    f"Week {item['_id']}"
                )

                values.append(
                    item["total_revenue"]
                )

            return {

                "labels": labels,

                "values": values
            }

        # =====================================================
        # CURRENT WEEK / LAST WEEK
        # =====================================================

        if filter == "current":

            today = datetime.now()

            start_date = datetime(
                today.year,
                today.month,
                today.day
            ) - timedelta(days=today.weekday())

        elif filter == "last":

            current_week_start = datetime(
                today.year,
                today.month,
                today.day
            ) - timedelta(days=today.weekday())

            start_date = current_week_start - timedelta(days=7)

            today = current_week_start

        else:

            start_date = today - timedelta(days=today.weekday())

        # =====================================================
        # WEEKLY PIPELINE
        # =====================================================

        pipeline = [

            {
                "$match": {

                    "billing_time": {

                        "$gte": start_date,
                        "$lt": today + timedelta(days=1)
                    }
                }
            },

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

        # =====================================================
        # DAY MAP
        # =====================================================

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

        # =====================================================
        # STORE VALUES
        # =====================================================

        for item in result:

            day = day_map.get(item["_id"])

            if day:

                weekly_data[day] = item["total_revenue"]

        # =====================================================
        # RETURN RESPONSE
        # =====================================================

        return {

            "labels": [

                "Mon",
                "Tue",
                "Wed",
                "Thu",
                "Fri",
                "Sat",
                "Sun"
            ],

            "values": [

                weekly_data["Mon"],
                weekly_data["Tue"],
                weekly_data["Wed"],
                weekly_data["Thu"],
                weekly_data["Fri"],
                weekly_data["Sat"],
                weekly_data["Sun"]
            ]
        }

    except Exception as e:

        return {
            "error": str(e)
        }