from fastapi import APIRouter, HTTPException
from pymongo.errors import PyMongoError

from app.mongodb import log_collection


router = APIRouter(
    prefix="/logs",
    tags=["Logs"]
)


# ============================================================
# VEHICLE TYPE FROM FLOOR
# ============================================================

def get_vehicle_type(log):

    # Use stored vehicle type if available
    vehicle_type = log.get("vehicle_type")

    if vehicle_type:
        return vehicle_type

    # Derive type from floor for older records
    floor = str(
        log.get("floor") or ""
    ).strip().upper()

    floor_vehicle_map = {
        "B1": "Large Vehicle",
        "B2": "Mini Truck",
        "L1": "Four Wheeler",
        "L2": "Two Wheeler",
        "L3": "Two Wheeler"
    }

    return floor_vehicle_map.get(
        floor,
        "-"
    )


# ============================================================
# GET PARKING LOGS
# ============================================================

@router.get("/")
def get_logs(
    page: int = 1,
    limit: int = 500,
    vehicle_number: str = "",
    status: str = ""
):

    try:

        # ----------------------------------------------------
        # Validate pagination
        # ----------------------------------------------------

        if page < 1:
            raise HTTPException(
                status_code=400,
                detail="Page must be greater than or equal to 1"
            )

        if limit < 1 or limit > 500:
            raise HTTPException(
                status_code=400,
                detail="Limit must be between 1 and 500"
            )


        skip = (
            page - 1
        ) * limit


        # ----------------------------------------------------
        # Build query
        # ----------------------------------------------------

        query = {}


        # ----------------------------------------------------
        # Vehicle number search
        # ----------------------------------------------------

        search_value = (
            vehicle_number
            .strip()
        )


        if search_value:

            query["vehicle_number"] = {

                "$regex":
                    search_value,

                "$options":
                    "i"
            }


        # ----------------------------------------------------
        # Status filter
        # ----------------------------------------------------

        status_value = (
            status
            .strip()
            .lower()
        )


        if status_value == "occupied":

            query["exit_time"] = None


        elif status_value == "exited":

            query["exit_time"] = {
                "$ne": None
            }


        elif status_value:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Status must be "
                    "'occupied' or 'exited'"
                )
            )


        # ----------------------------------------------------
        # Count matching records
        # ----------------------------------------------------

        total = (
            log_collection
            .count_documents(query)
        )


        # ----------------------------------------------------
        # Fetch logs
        # ----------------------------------------------------

        logs = list(

            log_collection
            .find(
                query,
                {"_id": 0}
            )
            .sort(
                "entry_time",
                -1
            )
            .skip(skip)
            .limit(limit)

        )


        # ----------------------------------------------------
        # Format logs
        # ----------------------------------------------------

        result = []


        for log in logs:

            entry_time = (
                log.get("entry_time")
            )


            exit_time = (
                log.get("exit_time")
            )


            # Determine status

            status_result = (

                "exited"

                if exit_time

                else "occupied"

            )


            # Duration

            duration_minutes = (
                log.get(
                    "duration_minutes"
                )
            )


            if duration_minutes is not None:

                duration = (
                    f"{duration_minutes} mins"
                )

            else:

                duration = "-"


            # Vehicle type

            vehicle_type = (
                get_vehicle_type(log)
            )


            # Floor

            floor = (
                log.get("floor")
                or "-"
            )


            # Fee

            fee = (
                log.get("fee")
                or 0
            )


            # ------------------------------------------------
            # Final log object
            # ------------------------------------------------

            result.append(
                {
                    "vehicle_number": log.get("vehicle_number"),

                    "vehicle_type": get_vehicle_type(log),

                    "slot_id": log.get("slot_id"),

                    "floor": log.get("floor") or "-",

                    "entry_time": entry_time,

                    "exit_time": exit_time,

                    "duration": (
                        f"{duration_minutes} mins"
                        if duration_minutes is not None
                        else "-"
                    ),

                    "fee": log.get("fee") or 0,

                    "status": status_value
                }
            )


        # ----------------------------------------------------
        # Response
        # ----------------------------------------------------

        return {

            "page":
                page,

            "limit":
                limit,

            "count":
                len(result),

            "total":
                total,

            "pages":
                (
                    (total + limit - 1)
                    // limit
                    if total
                    else 0
                ),

            "logs":
                result

        }


    except HTTPException:
        raise


    except PyMongoError as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Database Error: {str(e)}"
            )
        )


    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Unexpected Error: {str(e)}"
            )
        )