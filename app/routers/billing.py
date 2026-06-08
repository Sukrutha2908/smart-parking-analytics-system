from fastapi import APIRouter

from app.models.billing_model import BillingModel

router = APIRouter(
prefix="/billing",
tags=["Billing"]
)

# Create Billing

@router.post("/")
def create_bill(bill: BillingModel):

    return {
        "message": "Billing Created Successfully",
        "data": bill
    }

# Get All Bills

@router.get("/")
def get_bills():

    return {
        "message": "All Billing Records"
    }

# Get Bill By Vehicle ID

@router.get("/{vehicle_id}")
def get_bill(vehicle_id: int):
    return {
    "message": f"Billing Details for Vehicle {vehicle_id}"
}
