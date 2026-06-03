from fastapi import APIRouter
from app.mongodb import parking_collection

router = APIRouter()

# Total vehicles
@router.get("/total-vehicles")
async def total_vehicles():

    count = await parking_collection.count_documents({})

    return {
        "total_vehicles": count
    }

# Occupied slots
@router.get("/occupied-slots")
async def occupied_slots():

    count = await parking_collection.count_documents(
        {"status": "Occupied"}
    )

    return {
        "occupied_slots": count
    }

# Total revenue
@router.get("/total-revenue")
async def total_revenue():

    revenue = 0

    async for document in parking_collection.find():

        revenue += document.get("billing_amount", 0)

    return {
        "total_revenue": revenue
    }