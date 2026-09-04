from fastapi import APIRouter, HTTPException
from pymongo.errors import PyMongoError

from app.mongodb import slot_collection


router = APIRouter()


# =========================================================
# CREATE SLOTS
# =========================================================

@router.post("/")
def create_slots():

    try:

        # Do not delete existing slots.
        # Main.py already initializes the 500 slots.

        existing_count = slot_collection.count_documents({})

        if existing_count > 0:

            return {
                "message": "Parking slots already exist",
                "total_slots": existing_count
            }


        floors = {
            "B1": 100,
            "B2": 100,
            "L1": 100,
            "L2": 100,
            "L3": 100
        }

        all_slots = []


        for floor, count in floors.items():

            for i in range(
                1,
                count + 1
            ):

                slot = {

                    "slot_number": i,

                    "slot_id":
                        f"{floor}-{i}",

                    "floor":
                        floor,

                    "status":
                        "free",

                    "vehicle_number":
                        None,

                    "vehicle_type":
                        None
                }

                all_slots.append(slot)


        result = slot_collection.insert_many(
            all_slots
        )


        return {

            "message":
                "Slots created successfully",

            "inserted_count":
                len(result.inserted_ids),

            "total_slots":
                len(all_slots)
        }


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
# GET ALL SLOTS
# =========================================================

@router.get("/")
def get_slots():

    try:

        slots = list(

            slot_collection
            .find(
                {},
                {
                    "_id": 0
                }
            )
            .sort([
                ("floor", 1),
                ("slot_number", 1)
            ])
        )


        return slots


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
# SLOT SUMMARY
# =========================================================

@router.get("/summary")
def get_slot_summary():

    try:

        total_slots = (
            slot_collection
            .count_documents({})
        )


        available_slots = (
            slot_collection
            .count_documents({
                "status": "free"
            })
        )


        occupied_slots = (
            slot_collection
            .count_documents({
                "status": "occupied"
            })
        )


        return {

            "total":
                total_slots,

            "free":
                available_slots,

            "occupied":
                occupied_slots
        }


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