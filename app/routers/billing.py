from fastapi import APIRouter, HTTPException
from pymongo.errors import PyMongoError

from app.models.billing_model import BillingModel

router = APIRouter(
    prefix="/billing",
    tags=["Billing"]
)

# Create Billing
@router.post("/")
def create_bill(bill: BillingModel):

    try:
        # Convert model to dictionary
        bill_dict = bill.model_dump()

        # Here you can insert into MongoDB later
        # result = billing_collection.insert_one(bill_dict)

        return {
            "message": "Billing Created Successfully",
            "data": bill_dict
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


# Get All Bills
@router.get("/")
def get_bills():

    try:
        # Example dummy data
        bills = []

        # Replace with MongoDB fetch later
        # bills = list(billing_collection.find({}, {"_id": 0}))

        if not bills:
            raise HTTPException(
                status_code=404,
                detail="No Billing Records Found"
            )

        return {
            "count": len(bills),
            "data": bills
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


# Get Bill By Vehicle ID
@router.get("/{vehicle_id}")
def get_bill(vehicle_id: int):

    try:
        # Example dummy data
        bill = None

        # Replace with MongoDB query later
        # bill = billing_collection.find_one(
        #     {"vehicle_id": vehicle_id},
        #     {"_id": 0}
        # )

        if not bill:
            raise HTTPException(
                status_code=404,
                detail=f"No Bill Found for Vehicle ID {vehicle_id}"
            )

        return {
            "data": bill
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