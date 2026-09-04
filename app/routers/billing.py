from fastapi import APIRouter, HTTPException
from pymongo.errors import PyMongoError

from app.models.billing_model import BillingModel
from app.mongodb import billing_collection


router = APIRouter(
    prefix="/billing",
    tags=["Billing"]
)


# =========================================================
# CREATE BILLING
# =========================================================

@router.post("/")
def create_bill(bill: BillingModel):

    try:

        bill_dict = bill.model_dump()

        result = billing_collection.insert_one(
            bill_dict
        )

        return {
            "message": "Billing Created Successfully",
            "inserted_id": str(
                result.inserted_id
            ),
            "data": bill_dict
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
# GET ALL BILLS
# =========================================================

@router.get("/")
def get_bills():

    try:

        bills = list(
            billing_collection.find(
                {},
                {"_id": 0}
            ).sort(
                "billing_time",
                -1
            )
        )

        return bills

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
# GET BILL BY VEHICLE NUMBER
# =========================================================

@router.get("/{vehicle_number}")
def get_bill(
    vehicle_number: str
):

    try:

        vehicle_number = (
            vehicle_number
            .strip()
            .upper()
        )

        if not vehicle_number:

            raise HTTPException(
                status_code=400,
                detail="Vehicle number is required"
            )

        bill = billing_collection.find_one(
            {
                "vehicle_number":
                    vehicle_number
            },
            {
                "_id": 0
            },
            sort=[
                (
                    "billing_time",
                    -1
                )
            ]
        )

        if not bill:

            raise HTTPException(
                status_code=404,
                detail=(
                    f"No Bill Found for "
                    f"{vehicle_number}"
                )
            )

        return {
            "data": bill
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