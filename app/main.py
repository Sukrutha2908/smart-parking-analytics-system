from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Routers

from app.routers import parking
from app.routers import vehicle
from app.routers import slots
from app.routers import billing
from app.routers import transaction
from app.routers import analytics

# FastAPI App

app = FastAPI(
title="Smart Parking Analytics System",
version="1.0.0",
description="Real-Time Smart Parking Management System"
)

# Static Files

app.mount(
"/static",
StaticFiles(directory="app/static"),
name="static"
)

# Include Routers

app.include_router(parking.router)
app.include_router(vehicle.router)
app.include_router(slots.router)
app.include_router(billing.router)
app.include_router(transaction.router)
app.include_router(analytics.router)

# Home API

@app.get("/")
def home():
    return {
        "message": "Smart Parking API Running 🚗"
    }

# Health Check API

@app.get("/health")
def health():
    return {
    "status": "healthy"
    }
# Favicon

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("app/static/favicon.ico")


from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from pymongo import MongoClient
from pydantic import BaseModel

from datetime import datetime
from uuid import uuid4

import os

# ─────────────────────────────────────────────
# FastAPI App
# ─────────────────────────────────────────────

app = FastAPI(title="Smart Parking Analytics System")

# ─────────────────────────────────────────────
# CORS
# ─────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# Static Frontend Files
# ─────────────────────────────────────────────

app.mount(
    "/frontend",
    StaticFiles(directory="frontend"),
    name="frontend"
)

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

TOTAL_SLOTS = 500
RATE_PER_HOUR = 20

# ─────────────────────────────────────────────
# Initialize Slots
# ─────────────────────────────────────────────

def initialize_slots():

    existing = slots_col.count_documents({})

    if existing == 0:

        slots = []

        for i in range(1, TOTAL_SLOTS + 1):

            slots.append({
                "slot_number": i,
                "status": "free"
            })

        slots_col.insert_many(slots)

initialize_slots()

# ─────────────────────────────────────────────
# Pydantic Model
# ─────────────────────────────────────────────

class VehicleIn(BaseModel):
    vehicle_number: str

# ─────────────────────────────────────────────
# Serve Frontend
# ─────────────────────────────────────────────

@app.get("/")
def home():
    return FileResponse("frontend/index.html")

# ─────────────────────────────────────────────
# Get Slots
# ─────────────────────────────────────────────

@app.get("/slots")
def get_slots():

    slots = list(
        slots_col.find(
            {},
            {
                "_id": 0
            }
        )
    )

    return slots

# ─────────────────────────────────────────────
# Slot Summary
# ─────────────────────────────────────────────

@app.get("/slots/summary")
def slots_summary():

    free = slots_col.count_documents({
        "status": "free"
    })

    occupied = slots_col.count_documents({
        "status": "occupied"
    })

    return {
        "total": TOTAL_SLOTS,
        "free": free,
        "occupied": occupied
    }

# ─────────────────────────────────────────────
# Vehicle Entry
# ─────────────────────────────────────────────

@app.post("/entry")
def vehicle_entry(body: VehicleIn):

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
        "slot_number": slot["slot_number"],
        "entry_time": entry_time,
        "exit_time": None,
        "fee": None
    })

    return {
        "message": "Vehicle parked successfully",
        "slot_number": slot["slot_number"],
        "entry_time": entry_time
    }

# ─────────────────────────────────────────────
# Vehicle Exit
# ─────────────────────────────────────────────

@app.post("/exit")
def vehicle_exit(body: VehicleIn):

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

    # Update Parking Log

    logs_col.update_one(
        {"_id": log["_id"]},
        {
            "$set": {
                "exit_time": exit_time,
                "fee": fee
            }
        }
    )

    # Free Slot

    slots_col.update_one(
        {
            "slot_number": log["slot_number"]
        },
        {
            "$set": {
                "status": "free"
            }
        }
    )

    # ─────────────────────────────────────────
    # Billing Record
    # ─────────────────────────────────────────

    billing_id = str(uuid4())

    billing_data = {

        "billing_id": billing_id,

        "vehicle_number": vehicle_number,

        "slot_number": log["slot_number"],

        "entry_time": log["entry_time"],

        "exit_time": exit_time,

        "duration_hours": round(hours, 2),

        "rate_per_hour": RATE_PER_HOUR,

        "total_fee": fee,

        "created_at": datetime.utcnow()
    }

    billing_col.insert_one(billing_data)

    # ─────────────────────────────────────────
    # Transaction Record
    # ─────────────────────────────────────────

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

        "slot_number": log["slot_number"],

        "fee": fee,

        "billing_id": billing_id
    }

# ─────────────────────────────────────────────
# Parking Logs
# ─────────────────────────────────────────────

@app.get("/logs")
def get_logs(
    page: int = 1,
    limit: int = 50,
    status: str = None
):

    query = {}

    if status == "active":
        query["exit_time"] = None

    elif status == "completed":
        query["exit_time"] = {
            "$ne": None
        }

    total = logs_col.count_documents(query)

    docs = (
        logs_col.find(query)
        .sort("entry_time", -1)
        .skip((page - 1) * limit)
        .limit(limit)
    )

    results = []

    for d in docs:

        results.append({
            "vehicle_number": d["vehicle_number"],
            "slot_number": d["slot_number"],
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

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "logs": results
    }

# ─────────────────────────────────────────────
# Cleanup Logs
# ─────────────────────────────────────────────

@app.delete("/logs/cleanup")
def cleanup_logs():

    result = logs_col.delete_many({
        "exit_time": {"$ne": None}
    })

    return {
        "deleted": result.deleted_count
    }

# ─────────────────────────────────────────────
# Reset System
# ─────────────────────────────────────────────

@app.post("/reset")
def reset_system():

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
