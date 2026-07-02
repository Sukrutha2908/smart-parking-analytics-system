from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pymongo import MongoClient
from pydantic import BaseModel
from fastapi import WebSocket
from app.websocket_manager import manager

from fastapi import Request
from fastapi.templating import Jinja2Templates

from fastapi import WebSocket
from app.websocket_manager import manager

from fastapi import Request
from fastapi.templating import Jinja2Templates

from datetime import datetime
from uuid import uuid4

import os

from app.routers.analytics import router as analytics_router

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
app.mount(
    "/static",
    StaticFiles(directory="frontend"),
    name="static"
)


@app.get("/")
def home():
    return FileResponse("frontend/index.html")
templates = Jinja2Templates(
    directory="templates"
)
    

@app.websocket("/ws")

async def websocket_endpoint(

    websocket: WebSocket
):

    await manager.connect(
        websocket
    )

    try:

        while True:

            await websocket.receive_text()

    except:

        manager.disconnect(
            websocket
        )


templates = Jinja2Templates(
    directory="templates"
)
    

@app.websocket("/ws")

async def websocket_endpoint(

    websocket: WebSocket
):

    await manager.connect(
        websocket
    )

    try:

        while True:

            await websocket.receive_text()

    except:

        manager.disconnect(
            websocket
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

app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# ─────────────────────────────────────────────
# Home API
# ─────────────────────────────────────────────

@app.get("/")
async def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "title": "Smart Parking Dashboard"
        }
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
app.include_router(
    slots.router,
    prefix="/slots",
    tags=["Slots"]
)
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

class VehicleEntry(BaseModel):

    vehicle_number: str

    vehicle_type: str


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
# Vehicle Entry
# ─────────────────────────────────────────────

from datetime import datetime

# Vehicle Type → Allowed Floors

vehicle_floor_map = {

    "Large Vehicle": ["B1"],

    "Mini Truck": ["B2"],

    "Four Wheeler": ["L1"],

    "Two Wheeler": ["L2", "L3"]
}


# Vehicle Entry

@app.post("/entry")
def vehicle_entry(data: VehicleEntry):

    print(data)

    try:

        vehicle_number = data.vehicle_number.strip().upper()

        vehicle_type = data.vehicle_type

        if not vehicle_number or not vehicle_type:

            return {
                "error": "Vehicle Number and Vehicle Type required"
            }

        # Validate vehicle type

        allowed_floors = vehicle_floor_map.get(vehicle_type)

        if not allowed_floors:

            return {
                "error": "Invalid Vehicle Type"
            }

        # Check if vehicle already parked

        existing = logs_col.find_one({

            "vehicle_number": vehicle_number,

            "exit_time": None
        })

        if existing:

            return {
                "error": "Vehicle already parked"
            }

        # Find free slot only in allowed floors

        slot = slots_col.find_one({

            "floor": {"$in": allowed_floors},

            "status": "free"
        })

        if not slot:

            return {
                "error": f"No slots available for {vehicle_type}"
            }

        # Update slot status

        slots_col.update_one(

            {"slot_id": slot["slot_id"]},

            {
                "$set": {
                    "status": "occupied",
                    "vehicle_number": vehicle_number
                }
            }
        )

        # Create parking log

        log_data = {

            "vehicle_number": vehicle_number,

            "vehicle_type": vehicle_type,

            "slot_id": slot["slot_id"],

            "floor": slot["floor"],

            "entry_time": datetime.utcnow(),

            "exit_time": None,

            "duration_minutes": None,

            "fee": None
        }

        logs_col.insert_one(log_data)

        return {

            "message": "Vehicle Parked Successfully",

            "vehicle_number": vehicle_number,

            "vehicle_type": vehicle_type,

            "slot_allocated": slot["slot_id"],

            "floor": slot["floor"]
        }

    except Exception as e:

        return {
            "error": str(e)
        }

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

        duration_minutes = round(hours * 60)

        fee = round(duration_minutes / 60 * 20)

        logs_col.update_one(
            {"_id": log["_id"]},
            {
                "$set": {
                    "exit_time": exit_time,
                    "fee": fee,

                    "duration_minutes":
                        round(hours * 60)
                }
            }
        )

        slots_col.update_one(
            {
                "slot_id": log["slot_id"]
            },
            {
                "$set": {
                    "status": "free",
                    "vehicle_number": None
                }
            }
        )

        billing_id = str(uuid4())

        billing_data = {

            "billing_id": billing_id,

            "vehicle_number": vehicle_number,

            "slot_id": log["slot_id"],

            "floor": log.get("floor", "N/A"),

            "entry_time": log["entry_time"],

            "exit_time": exit_time,

            "duration_hours": round(hours, 2),

            "rate_per_hour": RATE_PER_HOUR,

            "amount": fee,

            "billing_time": datetime.utcnow()
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

            "floor": log.get("floor", "N/A"),

            "entry_time": str(log.get("entry_time")),

            "exit_time": str(exit_time),

            "duration_minutes": round(hours * 60),

            "rate_per_hour": RATE_PER_HOUR,

            "fee": fee,

            "billing_id": billing_id
        }

    except HTTPException as e:
        raise e

    except Exception as e:

        print("EXIT ERROR:", str(e))

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# ─────────────────────────────────────────────
# Parking Logs
# ─────────────────────────────────────────────

@app.get("/logs")
def get_logs(
    page: int = 1,
    limit: int = 50,
    vehicle_number: str = None,
    status: str = None
):

    try:

        skip = (page - 1) * limit

        query = {}

        # Vehicle Search
        if vehicle_number:

            query["vehicle_number"] = {
                "$regex": vehicle_number,
                "$options": "i"
            }

        # Status Filter
        if status:

            if status == "occupied":

                query["exit_time"] = None

            elif status == "exited":

                query["exit_time"] = {
                    "$ne": None
                }

        docs = list(
            logs_col.find(query, {"_id": 0})
            .sort("entry_time", -1)
            .skip(skip)
            .limit(limit)
        )

        results = []

        for d in docs:

            results.append({

                "vehicle_number":
                    d.get("vehicle_number"),

                "slot_id":
                    d.get("slot_id"),

                "floor":
                    d.get("floor"),

                "status":
                    "exited"
                    if d.get("exit_time")
                    else "occupied",

                "entry_time":
                    d["entry_time"].isoformat()
                    if d.get("entry_time")
                    else None,

                "exit_time":
                    d["exit_time"].isoformat()
                    if d.get("exit_time")
                    else None,

                "fee":
                    d.get("fee"),

                "duration":
                    f"{round(d.get('duration_minutes', 0))} mins"
                    if d.get("duration_minutes")
                    else "-"
            })

        total = logs_col.count_documents(query)

        return {

            "logs": results,

            "total": total,

            "page": page,

            "limit": limit,

            "total_pages":
                (total + limit - 1) // limit
        }

    except Exception as e:

        return {
            "error": str(e)
        }