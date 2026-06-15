from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from pymongo import MongoClient
from pydantic import BaseModel

from datetime import datetime
from uuid import uuid4

import os

# ─────────────────────────────────────────────
# Import Routers
# ─────────────────────────────────────────────

from app.routers import parking
from app.routers import vehicle
from app.routers import slots
from app.routers import billing
from app.routers import transaction
from app.routers import analytics

# ─────────────────────────────────────────────
# FastAPI App
# ─────────────────────────────────────────────

app = FastAPI(
    title="Smart Parking Analytics System",
    version="1.0.0",
    description="Real-Time Smart Parking Management System"
)

# ─────────────────────────────────────────────
# CORS Middleware
# ─────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# Static Files
# ─────────────────────────────────────────────

app.mount(
    "/frontend",
    StaticFiles(directory="frontend"),
    name="frontend"
)

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static"
)

# ─────────────────────────────────────────────
# Include Routers
# ─────────────────────────────────────────────

app.include_router(parking.router)
app.include_router(vehicle.router)
app.include_router(slots.router)
app.include_router(billing.router)
app.include_router(transaction.router)
app.include_router(analytics.router)

# ─────────────────────────────────────────────
# MongoDB Connection
# ─────────────────────────────────────────────

MONGODB_URL = os.getenv(
    "MONGODB_URL",
    "mongodb://localhost:27017/"
)

client = MongoClient(MONGODB_URL)

db = client["smart_parking"]

slots_col = db["slots"]
vehicles_col = db["vehicles"]
logs_col = db["parking_logs"]

billing_col = db["billing"]
transaction_col = db["transactions"]

print("MongoDB Connected Successfully")

# ─────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────

FLOORS = ["B1", "B2", "L1", "L2", "L3"]

SLOTS_PER_FLOOR = 100

RATE_PER_HOUR = 20

# ─────────────────────────────────────────────
# Initialize Multi-Layer Slots
# ─────────────────────────────────────────────

def initialize_slots():

    try:

        existing = slots_col.count_documents({})

        if existing == 0:

            slots_data = []

            for floor in FLOORS:

                for i in range(1, SLOTS_PER_FLOOR + 1):

                    slots_data.append({

                        "floor": floor,

                        "slot_number": i,

                        "slot_id": f"{floor}-{i}",

                        "status": "free"
                    })

            slots_col.insert_many(slots_data)

            print("Multi-Layer Slots Initialized Successfully")

    except Exception as e:

        print(f"Slot Initialization Error: {str(e)}")

initialize_slots()

# ─────────────────────────────────────────────
# Pydantic Model
# ─────────────────────────────────────────────

class VehicleIn(BaseModel):
    vehicle_number: str

# ─────────────────────────────────────────────
# Home API
# ─────────────────────────────────────────────

@app.get("/")
def home():
    return FileResponse("frontend/index.html")

# ─────────────────────────────────────────────
# Favicon API
# ─────────────────────────────────────────────

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("app/static/favicon.ico")

# ─────────────────────────────────────────────
# Health Check API
# ─────────────────────────────────────────────

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }

# ─────────────────────────────────────────────
# Slot Summary
# ─────────────────────────────────────────────

@app.get("/slots/summary")
def slots_summary():

    try:

        free = slots_col.count_documents({
            "status": "free"
        })

        occupied = slots_col.count_documents({
            "status": "occupied"
        })

        total = len(FLOORS) * SLOTS_PER_FLOOR

        return {
            "total": total,
            "free": free,
            "occupied": occupied
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Summary Error: {str(e)}"
        )

# ─────────────────────────────────────────────
# Vehicle Entry
# ─────────────────────────────────────────────

@app.post("/entry")
def vehicle_entry(body: VehicleIn):

    try:

        vehicle_number = body.vehicle_number.strip().upper()

        existing = logs_col.find_one({
            "vehicle_number": vehicle_number,
            "exit_time": None
        })

        if existing:

            raise HTTPException(
                status_code=409,
                detail="Vehicle already parked."
            )

        slot = slots_col.find_one_and_update(
            {"status": "free"},
            {"$set": {"status": "occupied"}}
        )

        if not slot:

            raise HTTPException(
                status_code=400,
                detail="No free slots available."
            )

        entry_time = datetime.utcnow()

        logs_col.insert_one({

            "vehicle_number": vehicle_number,

            "slot_id": slot["slot_id"],

            "floor": slot["floor"],

            "entry_time": entry_time,

            "exit_time": None,

            "fee": None
        })

        return {

            "message": "Vehicle parked successfully",

            "slot_id": slot["slot_id"],

            "floor": slot["floor"],

            "entry_time": entry_time
        }

    except HTTPException as e:
        raise e

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Vehicle Entry Error: {str(e)}"
        )

# ─────────────────────────────────────────────
# Vehicle Exit
# ─────────────────────────────────────────────

@app.post("/exit")
def vehicle_exit(body: VehicleIn):

    try:

        vehicle_number = body.vehicle_number.strip().upper()

        log = logs_col.find_one({
            "vehicle_number": vehicle_number,
            "exit_time": None
        })

        if not log:

            raise HTTPException(
                status_code=404,
                detail="Vehicle not found."
            )

        exit_time = datetime.utcnow()

        duration_seconds = (
            exit_time - log["entry_time"]
        ).total_seconds()

        hours = max(duration_seconds / 3600, 0.25)

        fee = round(hours * RATE_PER_HOUR, 2)

        logs_col.update_one(
            {"_id": log["_id"]},
            {
                "$set": {
                    "exit_time": exit_time,
                    "fee": fee
                }
            }
        )

        slots_col.update_one(
            {
                "slot_id": log["slot_id"]
            },
            {
                "$set": {
                    "status": "free"
                }
            }
        )

        billing_id = str(uuid4())

        billing_data = {

            "billing_id": billing_id,

            "vehicle_number": vehicle_number,

            "slot_id": log["slot_id"],

            "floor": log["floor"],

            "entry_time": log["entry_time"],

            "exit_time": exit_time,

            "duration_hours": round(hours, 2),

            "rate_per_hour": RATE_PER_HOUR,

            "total_fee": fee,

            "created_at": datetime.utcnow()
        }

        billing_col.insert_one(billing_data)

        transaction_data = {

            "transaction_id": str(uuid4()),

            "billing_id": billing_id,

            "vehicle_number": vehicle_number,

            "amount": fee,

            "payment_status": "paid",

            "payment_method": "cash",

            "transaction_time": datetime.utcnow()
        }

        transaction_col.insert_one(transaction_data)

        return {

            "message": "Vehicle exited successfully",

            "vehicle_number": vehicle_number,

            "slot_id": log["slot_id"],

            "floor": log["floor"],

            "entry_time": log["entry_time"].isoformat(),

            "exit_time": exit_time.isoformat(),

            "duration_minutes": round(hours * 60),

            "rate_per_hour": RATE_PER_HOUR,

            "fee": fee,

            "billing_id": billing_id
        }

    except HTTPException as e:
        raise e

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Vehicle Exit Error: {str(e)}"
        )

# ─────────────────────────────────────────────
# Parking Logs
# ─────────────────────────────────────────────

@app.get("/logs")
def get_logs():

    try:

        docs = logs_col.find().sort("entry_time", -1)

        results = []

        for d in docs:

            results.append({

                "vehicle_number": d["vehicle_number"],

                "slot_id": d["slot_id"],

                "floor": d["floor"],

                "entry_time": (
                    d["entry_time"].isoformat()
                    if d.get("entry_time")
                    else None
                ),

                "exit_time": (
                    d["exit_time"].isoformat()
                    if d.get("exit_time")
                    else None
                ),

                "fee": d.get("fee")
            })

        return results

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Logs Error: {str(e)}"
        )

# ─────────────────────────────────────────────
# Cleanup Logs
# ─────────────────────────────────────────────

@app.delete("/logs/cleanup")
def cleanup_logs():

    try:

        result = logs_col.delete_many({
            "exit_time": {"$ne": None}
        })

        return {
            "deleted": result.deleted_count
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Cleanup Error: {str(e)}"
        )

# ─────────────────────────────────────────────
# Reset System
# ─────────────────────────────────────────────

@app.post("/reset")
def reset_system():

    try:

        slots_col.update_many(
            {},
            {
                "$set": {
                    "status": "free"
                }
            }
        )

        logs_col.delete_many({})
        vehicles_col.delete_many({})

        return {
            "message": "System reset successful"
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Reset Error: {str(e)}"
        )