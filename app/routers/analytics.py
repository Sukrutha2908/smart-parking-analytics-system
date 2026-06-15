from fastapi import APIRouter, HTTPException

from app.mongodb import (
    slots_collection,
    transaction_collection,
    parking_collection
)

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)

# ─────────────────────────────────────────────
# Parking Occupancy
# ─────────────────────────────────────────────

@router.get("/occupancy")
def parking_occupancy():

    try:

        total = slots_collection.count_documents({})

        occupied = slots_collection.count_documents({
            "status": "occupied"
        })

        rate = 0

        if total > 0:

            rate = round((occupied / total) * 100, 2)

        return {
            "total_slots": total,
            "occupied_slots": occupied,
            "occupancy_rate": f"{rate}%"
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# ─────────────────────────────────────────────
# Revenue Analytics
# ─────────────────────────────────────────────

@router.get("/revenue")
def revenue():

    try:

        transactions = list(
            transaction_collection.find({})
        )

        total = 0

        for t in transactions:

            total += t.get("amount", 0)

        return {
            "total_revenue": total,
            "transactions": len(transactions)
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# ─────────────────────────────────────────────
# Peak Hour Analytics
# ─────────────────────────────────────────────

@router.get("/peak-hours")
def peak_hours():

    try:

        logs = list(
            parking_collection.find({})
        )

        hours = {}

        for log in logs:

            if log.get("entry_time"):

                hour = log["entry_time"].hour

                hours[hour] = hours.get(hour, 0) + 1

        if not hours:

            return {
                "peak_hour": "No Data"
            }

        peak = max(hours, key=hours.get)

        return {
            "peak_hour": f"{peak}:00 - {peak+1}:00",
            "vehicle_count": hours[peak]
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# ─────────────────────────────────────────────
# Vehicle Count Analytics
# ─────────────────────────────────────────────

@router.get("/vehicle-count")
def vehicle_count():

    try:

        total = parking_collection.count_documents({})

        active = parking_collection.count_documents({
            "exit_time": None
        })

        completed = parking_collection.count_documents({
            "exit_time": {
                "$ne": None
            }
        })

        return {

            "total_vehicles": total,

            "currently_parked": active,

            "completed_parking": completed
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )