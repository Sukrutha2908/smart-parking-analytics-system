from fastapi import APIRouter, HTTPException
from pymongo.errors import PyMongoError

from app.mongodb import log_collection

router = APIRouter(
    prefix="/logs",
    tags=["Logs"]
)


@router.get("/")
def get_logs(page: int = 1, limit: int = 50):

    try:
        skip = (page - 1) * limit

        logs = list(
            log_collection.find({}, {"_id": 0})
            .skip(skip)
            .limit(limit)
        )

        return logs

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