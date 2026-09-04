from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException
from pymongo.errors import PyMongoError

from app.mongodb import (
    billing_collection,
    log_collection,
    slot_collection,
)


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


# =========================================================
# HELPERS
# =========================================================

def _day_map():
    return {
        1: "Sun",
        2: "Mon",
        3: "Tue",
        4: "Wed",
        5: "Thu",
        6: "Fri",
        7: "Sat",
    }


def _week_labels():
    return [
        "Mon",
        "Tue",
        "Wed",
        "Thu",
        "Fri",
        "Sat",
        "Sun",
    ]


def _get_date_range(filter_name: str):
    """
    Returns a UTC date range for the requested revenue filter.

    The application stores billing_time as a MongoDB datetime.
    This uses the current server date while grouping/displaying
    in Asia/Kolkata elsewhere.
    """

    now = datetime.now(timezone.utc)

    today = now.date()

    # Monday = 0
    monday = today - timedelta(days=today.weekday())

    if filter_name == "last":
        start_date = monday - timedelta(days=7)
        end_date = monday

    elif filter_name == "month":
        start_date = today.replace(day=1)

        if start_date.month == 12:
            next_month = start_date.replace(
                year=start_date.year + 1,
                month=1,
                day=1,
            )
        else:
            next_month = start_date.replace(
                month=start_date.month + 1,
                day=1,
            )

        end_date = next_month

    else:
        # current week
        start_date = monday
        end_date = monday + timedelta(days=7)

    start_dt = datetime.combine(
        start_date,
        datetime.min.time(),
        tzinfo=timezone.utc,
    )

    end_dt = datetime.combine(
        end_date,
        datetime.min.time(),
        tzinfo=timezone.utc,
    )

    return start_dt, end_dt


# =========================================================
# OCCUPANCY
# =========================================================

@router.get("/occupancy")
def parking_occupancy():

    try:

        total_slots = slot_collection.count_documents({})

        occupied_slots = slot_collection.count_documents({
            "status": "occupied"
        })

        if total_slots == 0:
            raise HTTPException(
                status_code=404,
                detail="No parking slot data found",
            )

        available_slots = total_slots - occupied_slots

        occupancy_rate = (
            occupied_slots / total_slots
        ) * 100

        return {
            "total_slots": total_slots,
            "occupied_slots": occupied_slots,
            "available_slots": available_slots,
            "occupancy_rate": round(
                occupancy_rate,
                2,
            ),
        }

    except HTTPException:
        raise

    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database Error: {str(e)}",
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected Error: {str(e)}",
        )


# =========================================================
# REVENUE
# =========================================================

@router.get("/revenue")
def revenue():

    try:

        pipeline = [
            {
                "$match": {
                    "billing_time": {
                        "$exists": True,
                        "$ne": None,
                    },
                    "amount": {
                        "$exists": True,
                        "$ne": None,
                    },
                }
            },
            {
                "$group": {
                    "_id": {
                        "$dayOfWeek": {
                            "date": "$billing_time",
                            "timezone": "Asia/Kolkata",
                        }
                    },
                    "total_revenue": {
                        "$sum": "$amount",
                    },
                }
            },
        ]

        result = list(
            billing_collection.aggregate(pipeline)
        )

        day_map = _day_map()

        weekly_data = {
            day: 0
            for day in _week_labels()
        }

        for item in result:

            day = day_map.get(item.get("_id"))

            if day:
                weekly_data[day] = (
                    item.get("total_revenue") or 0
                )

        labels = _week_labels()

        return {
            "labels": labels,
            "values": [
                weekly_data[day]
                for day in labels
            ],
        }

    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database Error: {str(e)}",
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected Error: {str(e)}",
        )


# =========================================================
# WEEKLY REVENUE
# =========================================================

@router.get("/weekly-revenue")
def weekly_revenue(filter: str = "current"):

    try:

        if filter not in {
            "current",
            "last",
            "month",
        }:
            filter = "current"

        start_dt, end_dt = _get_date_range(filter)

        pipeline = [
            {
                "$match": {
                    "billing_time": {
                        "$gte": start_dt,
                        "$lt": end_dt,
                    },
                    "amount": {
                        "$exists": True,
                        "$ne": None,
                    },
                }
            },
            {
                "$group": {
                    "_id": {
                        "$dayOfWeek": {
                            "date": "$billing_time",
                            "timezone": "Asia/Kolkata",
                        }
                    },
                    "total_revenue": {
                        "$sum": "$amount",
                    },
                }
            },
        ]

        result = list(
            billing_collection.aggregate(pipeline)
        )

        day_map = _day_map()

        revenue_map = {
            day: 0
            for day in _week_labels()
        }

        for item in result:

            day = day_map.get(item.get("_id"))

            if day:
                revenue_map[day] = (
                    item.get("total_revenue") or 0
                )

        labels = _week_labels()

        return {
            "labels": labels,
            "values": [
                revenue_map[day]
                for day in labels
            ],
            "filter": filter,
        }

    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database Error: {str(e)}",
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected Error: {str(e)}",
        )


# =========================================================
# VEHICLE DISTRIBUTION
# =========================================================

@router.get("/vehicle-distribution")
def vehicle_distribution():

    try:

        pipeline = [
            {
                "$match": {
                    "vehicle_type": {
                        "$exists": True,
                        "$ne": None,
                    }
                }
            },
            {
                "$group": {
                    "_id": "$vehicle_type",
                    "count": {
                        "$sum": 1
                    },
                }
            },
        ]

        result = list(
            log_collection.aggregate(pipeline)
        )

        # Actual entry types used by /entry:
        #
        # Four Wheeler  -> Car
        # Two Wheeler   -> Bike
        # Mini Truck    -> Truck
        # Large Vehicle -> Truck

        cars = 0
        bikes = 0
        trucks = 0

        for item in result:

            vehicle_type = str(
                item.get("_id", "")
            ).strip().lower()

            count = int(
                item.get("count", 0) or 0
            )

            if vehicle_type in {
                "four wheeler",
                "four-wheeler",
                "car",
                "cars",
            }:
                cars += count

            elif vehicle_type in {
                "two wheeler",
                "two-wheeler",
                "bike",
                "bikes",
                "motorcycle",
            }:
                bikes += count

            elif vehicle_type in {
                "mini truck",
                "mini-truck",
                "large vehicle",
                "large-vehicle",
                "truck",
                "trucks",
            }:
                trucks += count

        total = cars + bikes + trucks

        if total == 0:
            return {
                "cars": 0,
                "bikes": 0,
                "trucks": 0,
                "car_percent": 0,
                "bike_percent": 0,
                "truck_percent": 0,
                "total": 0,
            }

        car_percent = round(
            cars / total * 100
        )

        bike_percent = round(
            bikes / total * 100
        )

        # Force the three displayed percentages to total 100.
        truck_percent = (
            100
            - car_percent
            - bike_percent
        )

        return {
            "cars": cars,
            "bikes": bikes,
            "trucks": trucks,
            "car_percent": car_percent,
            "bike_percent": bike_percent,
            "truck_percent": truck_percent,
            "total": total,
        }

    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database Error: {str(e)}",
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected Error: {str(e)}",
        )


# =========================================================
# PEAK HOURS
# =========================================================

@router.get("/peak-hours")
def peak_hours():

    try:

        pipeline = [
            {
                "$match": {
                    "entry_time": {
                        "$exists": True,
                        "$ne": None,
                    }
                }
            },
            {
                "$group": {
                    "_id": {
                        "$hour": {
                            "date": "$entry_time",
                            "timezone": "Asia/Kolkata",
                        }
                    },
                    "count": {
                        "$sum": 1
                    },
                }
            },
            {
                "$sort": {
                    "count": -1
                }
            },
            {
                "$limit": 1
            },
        ]

        result = list(
            log_collection.aggregate(pipeline)
        )

        if not result:
            raise HTTPException(
                status_code=404,
                detail="No peak hour data found",
            )

        return {
            "peak_hour": result[0].get("_id"),
            "vehicle_count": result[0].get("count", 0),
        }

    except HTTPException:
        raise

    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database Error: {str(e)}",
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected Error: {str(e)}",
        )


# =========================================================
# VEHICLE COUNT
# =========================================================

@router.get("/vehicle-count")
def vehicle_count():

    try:

        total_vehicles = (
            log_collection.count_documents({})
        )

        return {
            "total_vehicles": total_vehicles
        }

    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database Error: {str(e)}",
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected Error: {str(e)}",
        )
