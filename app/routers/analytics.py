from fastapi import APIRouter, HTTPException
from pymongo.errors import PyMongoError

from app.mongodb import (
    parking_collection,
    billing_collection,
    vehicle_collection,
    slot_collection
)


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


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
                detail="No parking slot data found"
            )

        occupancy_rate = (
            occupied_slots / total_slots
        ) * 100

        return {

            "total_slots":
                total_slots,

            "occupied_slots":
                occupied_slots,

            "available_slots":
                total_slots - occupied_slots,

            "occupancy_rate":
                round(occupancy_rate, 2)
        }

    except HTTPException:
        raise

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
# REVENUE
# =========================================================

@router.get("/revenue")
def revenue():

    try:

        pipeline = [

            {
                "$group": {

                    "_id": {
                        "$dayOfWeek": {
                            "date":
                                "$billing_time",

                            "timezone":
                                "Asia/Kolkata"
                        }
                    },

                    "total_revenue": {
                        "$sum": "$amount"
                    }
                }
            }
        ]

        result = list(
            billing_collection.aggregate(
                pipeline
            )
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

            day = day_map.get(
                item["_id"]
            )

            if day:

                weekly_data[day] = (
                    item["total_revenue"]
                )

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
# WEEKLY REVENUE
# =========================================================

@router.get("/weekly-revenue")
def weekly_revenue(filter: str = "current"):

    try:

        pipeline = [

            {
                "$group": {

                    "_id": {
                        "$dayOfWeek": {
                            "date":
                                "$billing_time",

                            "timezone":
                                "Asia/Kolkata"
                        }
                    },

                    "total_revenue": {
                        "$sum": "$amount"
                    }
                }
            }
        ]

        result = list(
            billing_collection.aggregate(
                pipeline
            )
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

        revenue_map = {

            "Mon": 0,
            "Tue": 0,
            "Wed": 0,
            "Thu": 0,
            "Fri": 0,
            "Sat": 0,
            "Sun": 0
        }

        for item in result:

            day = day_map.get(
                item["_id"]
            )

            if day:

                revenue_map[day] = (
                    item["total_revenue"]
                )

        labels = [
            "Mon",
            "Tue",
            "Wed",
            "Thu",
            "Fri",
            "Sat",
            "Sun"
        ]

        values = [
            revenue_map[day]
            for day in labels
        ]

        return {

            "labels": labels,

            "values": values,

            "filter": filter
        }

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
# VEHICLE DISTRIBUTION
# =========================================================

@router.get("/vehicle-distribution")
def vehicle_distribution():

    try:

        pipeline = [

            {
                "$group": {

                    "_id":
                        "$vehicle_type",

                    "count": {
                        "$sum": 1
                    }
                }
            }
        ]

        result = list(
            parking_collection.aggregate(
                pipeline
            )
        )

        counts = {

            "Car": 0,
            "Bike": 0,
            "Truck": 0
        }

        for item in result:

            vehicle_type = item["_id"]

            count = item["count"]

            if vehicle_type in counts:

                counts[
                    vehicle_type
                ] = count

        total = sum(
            counts.values()
        )

        if total == 0:

            return {

                "cars": 0,
                "bikes": 0,
                "trucks": 0,

                "car_percent": 0,
                "bike_percent": 0,
                "truck_percent": 0
            }

        car_percent = round(
            counts["Car"] /
            total * 100
        )

        bike_percent = round(
            counts["Bike"] /
            total * 100
        )

        truck_percent = round(
            counts["Truck"] /
            total * 100
        )

        return {

            "cars":
                counts["Car"],

            "bikes":
                counts["Bike"],

            "trucks":
                counts["Truck"],

            "car_percent":
                car_percent,

            "bike_percent":
                bike_percent,

            "truck_percent":
                truck_percent
        }

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
# PEAK HOURS
# =========================================================

@router.get("/peak-hours")
def peak_hours():

    try:

        pipeline = [

            {
                "$group": {

                    "_id":
                        "$entry_hour",

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
            parking_collection.aggregate(
                pipeline
            )
        )

        if not result:

            raise HTTPException(
                status_code=404,
                detail="No peak hour data found"
            )

        return {

            "peak_hour":
                result[0]["_id"],

            "vehicle_count":
                result[0]["count"]
        }

    except HTTPException:
        raise

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
# VEHICLE COUNT
# =========================================================

@router.get("/vehicle-count")
def vehicle_count():

    try:

        total_vehicles = (
            vehicle_collection
            .count_documents({})
        )

        return {

            "total_vehicles":
                total_vehicles
        }

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
# WEEKLY REVENUE
# =========================================================

@router.get("/weekly-revenue")
def weekly_revenue(filter: str = "current"):

    try:

        pipeline = [
            {
                "$match": {
                    "fee": {
                        "$ne": None
                    }
                }
            },
            {
                "$group": {
                    "_id": {
                        "$dayOfWeek": "$entry_time"
                    },
                    "revenue": {
                        "$sum": "$fee"
                    }
                }
            }
        ]

        result = list(
            parking_collection.aggregate(
                pipeline
            )
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

        revenue_data = {
            "Mon": 0,
            "Tue": 0,
            "Wed": 0,
            "Thu": 0,
            "Fri": 0,
            "Sat": 0,
            "Sun": 0
        }

        for item in result:

            day = day_map.get(
                item["_id"]
            )

            if day:

                revenue_data[day] = (
                    item["revenue"] or 0
                )

        return [
            {
                "day": day,
                "revenue": revenue_data[day]
            }

            for day in [
                "Mon",
                "Tue",
                "Wed",
                "Thu",
                "Fri",
                "Sat",
                "Sun"
            ]
        ]

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
                        "$ne": None
                    }
                }
            },

            {
                "$group": {

                    "_id": "$vehicle_type",

                    "count": {
                        "$sum": 1
                    }
                }
            }
        ]

        result = list(
            parking_collection.aggregate(
                pipeline
            )
        )

        counts = {

            "Car": 0,

            "Bike": 0,

            "Truck": 0
        }

        for item in result:

            vehicle_type = item["_id"]

            if vehicle_type in counts:

                counts[vehicle_type] = (
                    item["count"]
                )

        total = sum(
            counts.values()
        )

        if total == 0:

            return {
                "cars": 0,
                "bikes": 0,
                "trucks": 0
            }

        return {

            "cars": round(
                counts["Car"] / total * 100
            ),

            "bikes": round(
                counts["Bike"] / total * 100
            ),

            "trucks": round(
                counts["Truck"] / total * 100
            )
        }

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