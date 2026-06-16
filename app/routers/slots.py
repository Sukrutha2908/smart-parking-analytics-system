from fastapi import APIRouter
from app.mongodb import slot_collection

router = APIRouter()


# ---------------------------------------------------
# CREATE SLOTS
# ---------------------------------------------------

@router.post("/")
def create_slots():

    try:

        # Delete existing slots
        slot_collection.delete_many({})

        floors = {
            "B1": 100,
            "B2": 100,
            "L1": 100,
            "L2": 100,
            "L3": 100
        }

        all_slots = []

        for floor, count in floors.items():

            for i in range(1, count + 1):

                slot = {

                    "slot_number": i,

                    "slot_id": f"{floor}-{str(i).zfill(2)}",

                    "floor": floor,

                    "status": "free"
                }

                all_slots.append(slot)

        result = slot_collection.insert_many(all_slots)

        return {

            "message": "Slots created successfully",

            "inserted_count": len(result.inserted_ids),

            "total_slots": len(all_slots)
        }

    except Exception as e:

        return {

            "error": str(e)
        }


# ---------------------------------------------------
# GET ALL SLOTS
# ---------------------------------------------------

@router.get("/")
def get_slots():

    try:

        slots = list(
            slot_collection.find({}, {"_id": 0})
        )

        return slots

    except Exception as e:

        return {

            "error": str(e)
        }


# ---------------------------------------------------
# SLOT SUMMARY
# ---------------------------------------------------

@router.get("/summary")
def get_slot_summary():

    try:

        total_slots = slot_collection.count_documents({})

        available_slots = slot_collection.count_documents({
            "status": "free"
        })

        occupied_slots = slot_collection.count_documents({
            "status": "occupied"
        })

        return {
            
            "total": total_slots,
            
            "free": available_slots,
            
            "occupied": occupied_slots
        }

    except Exception as e:

        return {

            "error": str(e)
        }