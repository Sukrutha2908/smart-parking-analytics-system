from fastapi import APIRouter, HTTPException
from pymongo.errors import PyMongoError

from app.models.billing_model import BillingModel
from app.mongodb import billing_collection

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
        result = billing_collection.insert_one(bill_dict)

        return {
            "message": "Billing Created Successfully",
            "inserted_id": str(result.inserted_id),
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

        bills = list(
            billing_collection.find()
        )

        for bill in bills:

            bill["_id"] = str(
                bill["_id"]
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
    
    
    # Get Bill By Vehicle ID
@router.get("/{vehicle_number}")
def get_bill(vehicle_number: str):

    try:

        bills = billing_collection.find({

            "vehicle_number": vehicle_number.upper()
        })

        for bill in bills:
            bill["_id"] = str(bill["_id"])

            raise HTTPException(

                status_code=404,

                detail=f"No Bill Found for {vehicle_number}"
            )

        bill["_id"] = str(
            bill["_id"]
        )

        return bills

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