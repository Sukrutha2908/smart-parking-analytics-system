from fastapi import APIRouter, HTTPException
from pymongo.errors import PyMongoError

from app.mongodb import parking_collection

router = APIRouter(
    prefix="/logs",
    tags=["Logs"]
)


@router.get("/")
def get_logs(
    page: int = 1,
    limit: int = 50,
    vehicle_number: str = "",
    status: str = ""
):

    try:

        skip = (page - 1) * limit

        query = {}


        # Vehicle search
        if vehicle_number:

            query["vehicle_number"] = {
                "$regex": vehicle_number,
                "$options": "i"
            }


        # Status filter
        if status == "occupied":

            query["exit_time"] = None

        elif status == "exited":

            query["exit_time"] = {
                "$ne": None
            }


        logs = list(

            parking_collection
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


        result = []


        for log in logs:

            exit_time = log.get(
                "exit_time"
            )

            entry_time = log.get(
                "entry_time"
            )


            if exit_time:

                status_value = "exited"

            else:

                status_value = "occupied"


            result.append({

                "vehicle_number":
                    log.get(
                        "vehicle_number"
                    ),

                "slot_id":
                    log.get(
                        "slot_id"
                    ),

                "entry_time":
                    entry_time,

                "exit_time":
                    exit_time,

                "duration":
                    (
                        f"{log.get('duration_minutes')} mins"
                        if log.get(
                            "duration_minutes"
                        ) is not None
                        else "-"
                    ),

                "fee":
                    log.get(
                        "fee"
                    ) or 0,

                "status":
                    status_value
            })


        return result


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