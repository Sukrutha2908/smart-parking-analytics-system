from fastapi import APIRouter, HTTPException

from app.models.billing_model import BillingModel

router = APIRouter(
    prefix="/billing",
    tags=["Billing"]
)

# Create Billing

@router.post("/")
def create_bill(bill: BillingModel):

    try:

        bill_dict = bill.dict()

        return {
            "message": "Billing Created Successfully",
            "data": bill_dict
        }

    except HTTPException as e:
        raise e

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Unexpected Error: {str(e)}"
        )

# Get All Bills

@router.get("/")
def get_bills():

    try:

        bills = []

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

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Unexpected Error: {str(e)}"
        )

# Get Bill By Vehicle ID

@router.get("/{vehicle_id}")
def get_bill(vehicle_id: int):

    try:

        bill = None

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

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Unexpected Error: {str(e)}"
        )