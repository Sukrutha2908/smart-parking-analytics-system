from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from pydantic import BaseModel

from datetime import datetime
from uuid import uuid4

from dotenv import load_dotenv
import os

from app.websocket_manager import manager

# =========================================================
# ROUTERS
# =========================================================

from app.routers import parking
from app.routers import vehicle
from app.routers import slots
from app.routers import billing
from app.routers import transaction
from app.routers import analytics
from app.routers import auth


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()


# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI(
    title="Smart Parking Analytics System",
    version="1.0.0",
    description="Real-Time Smart Parking Management System"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# =========================================================
# STATIC FRONTEND FILES
# =========================================================

app.mount(
    "/static",
    StaticFiles(directory="frontend"),
    name="static"
)


# =========================================================
# AUTHENTICATION PAGES
# =========================================================
@app.get("/logout")
async def logout_page():
    return FileResponse("frontend/logout.html")

@app.get("/login")
def login_page():

    return FileResponse(
        "frontend/login.html"
    )


@app.get("/signup")
def signup_page():

    return FileResponse(
        "frontend/signup.html"
    )


@app.get("/forgot-password")
def forgot_password_page():

    return FileResponse(
        "frontend/forgot-password.html"
    )


@app.get("/reset-password")
def reset_password_page():

    return FileResponse(
        "frontend/reset-password.html"
    )


# =========================================================
# ROOT
# =========================================================

@app.get("/")
async def home():

    return RedirectResponse(
        url="/login"
    )


# =========================================================
# DASHBOARD
# =========================================================

@app.get("/dashboard")
async def dashboard():

    return FileResponse(
        "frontend/index.html"
    )


# =========================================================
# WEBSOCKET
# =========================================================

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

    except Exception:

        manager.disconnect(
            websocket
        )


# =========================================================
# INCLUDE ROUTERS
# =========================================================

app.include_router(
    parking.router
)

app.include_router(
    vehicle.router
)

app.include_router(
    slots.router,
    prefix="/slots",
    tags=["Slots"]
)

app.include_router(
    billing.router
)

app.include_router(
    transaction.router
)

app.include_router(
    analytics.router
)

# JWT Authentication
app.include_router(
    auth.router
)


# =========================================================
# MONGODB CONNECTION
# =========================================================

MONGODB_URL = os.getenv(
    "MONGODB_URL",
    "mongodb://localhost:27017/"
)

client = MongoClient(
    MONGODB_URL
)

db = client["smart_parking"]

slots_col = db["slots"]

vehicles_col = db["vehicles"]

logs_col = db["parking_logs"]

billing_col = db["billing"]

transaction_col = db["transactions"]


print(
    "MongoDB Connected Successfully"
)


# =========================================================
# CONSTANTS
# =========================================================

FLOORS = [
    "B1",
    "B2",
    "L1",
    "L2",
    "L3"
]

SLOTS_PER_FLOOR = 100

RATE_PER_HOUR = 20


# =========================================================
# INITIALIZE PARKING SLOTS
# =========================================================

def initialize_slots():

    try:

        existing = slots_col.count_documents({})

        if existing == 0:

            slots_data = []

            for floor in FLOORS:

                for i in range(
                    1,
                    SLOTS_PER_FLOOR + 1
                ):

                    slots_data.append({

                        "floor": floor,

                        "slot_number": i,

                        "slot_id":
                            f"{floor}-{i}",

                        "status": "free",

                        "vehicle_number":
                            None,

                        "vehicle_type":
                            None
                    })

            slots_col.insert_many(
                slots_data
            )

            print(
                "Multi-Layer Slots "
                "Initialized Successfully"
            )

        else:

            print(
                f"Existing slots found: "
                f"{existing}"
            )

    except Exception as e:

        print(
            f"Slot Initialization Error: "
            f"{str(e)}"
        )


initialize_slots()


# =========================================================
# PYDANTIC MODELS
# =========================================================

class VehicleIn(BaseModel):

    vehicle_number: str


class VehicleEntry(BaseModel):

    vehicle_number: str

    vehicle_type: str


# =========================================================
# FAVICON
# =========================================================

@app.get(
    "/favicon.ico",
    include_in_schema=False
)
async def favicon():

    return FileResponse(
        "app/static/favicon.ico"
    )


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# =========================================================
# VEHICLE TYPE → FLOOR
# =========================================================

vehicle_floor_map = {

    "Large Vehicle": [
        "B1"
    ],

    "Mini Truck": [
        "B2"
    ],

    "Four Wheeler": [
        "L1"
    ],

    "Two Wheeler": [
        "L2",
        "L3"
    ]
}


# =========================================================
# VEHICLE ENTRY
# =========================================================

@app.post("/entry")
def vehicle_entry(
    data: VehicleEntry
):

    try:

        vehicle_number = (
            data.vehicle_number
            .strip()
            .upper()
        )

        vehicle_type = (
            data.vehicle_type
        )


        # ---------------------------------------------
        # VALIDATION
        # ---------------------------------------------

        if not vehicle_number:

            return {
                "error":
                    "Vehicle Number required"
            }


        if not vehicle_type:

            return {
                "error":
                    "Vehicle Type required"
            }


        # ---------------------------------------------
        # CHECK VEHICLE TYPE
        # ---------------------------------------------

        allowed_floors = (
            vehicle_floor_map.get(
                vehicle_type
            )
        )


        if not allowed_floors:

            return {
                "error":
                    "Invalid Vehicle Type"
            }


        # ---------------------------------------------
        # CHECK EXISTING VEHICLE
        # ---------------------------------------------

        existing = logs_col.find_one({

            "vehicle_number":
                vehicle_number,

            "exit_time":
                None
        })


        if existing:

            return {
                "error":
                    "Vehicle already parked"
            }


        # ---------------------------------------------
        # FIND FREE SLOT
        # ---------------------------------------------

        slot = slots_col.find_one({

            "floor": {
                "$in":
                    allowed_floors
            },

            "status":
                "free"
        })


        if not slot:

            return {
                "error":
                    f"No slots available "
                    f"for {vehicle_type}"
            }


        # ---------------------------------------------
        # UPDATE SLOT
        # ---------------------------------------------

        slots_col.update_one(

            {
                "slot_id":
                    slot["slot_id"]
            },

            {
                "$set": {

                    "status":
                        "occupied",

                    "vehicle_number":
                        vehicle_number,

                    "vehicle_type":
                        vehicle_type
                }
            }
        )


        # ---------------------------------------------
        # CREATE PARKING LOG
        # ---------------------------------------------

        entry_time = datetime.utcnow()


        log_data = {

            "vehicle_number":
                vehicle_number,

            "vehicle_type":
                vehicle_type,

            "slot_id":
                slot["slot_id"],

            "floor":
                slot["floor"],

            "entry_time":
                entry_time,

            "exit_time":
                None,

            "duration_minutes":
                None,

            "fee":
                0
        }


        logs_col.insert_one(
            log_data
        )


        return {

            "message":
                "Vehicle Parked Successfully",

            "vehicle_number":
                vehicle_number,

            "vehicle_type":
                vehicle_type,

            "slot_allocated":
                slot["slot_id"],

            "floor":
                slot["floor"]
        }


    except Exception as e:

        return {
            "error":
                str(e)
        }


# =========================================================
# VEHICLE EXIT
# =========================================================

@app.post("/exit")
def vehicle_exit(
    body: VehicleIn
):

    try:

        vehicle_number = (
            body.vehicle_number
            .strip()
            .upper()
        )


        # ---------------------------------------------
        # FIND PARKING LOG
        # ---------------------------------------------

        log = logs_col.find_one({

            "vehicle_number":
                vehicle_number,

            "exit_time":
                None
        })


        if not log:

            raise HTTPException(
                status_code=404,
                detail="Vehicle not found."
            )


        # ---------------------------------------------
        # EXIT TIME
        # ---------------------------------------------

        exit_time = datetime.utcnow()


        duration_seconds = (

            exit_time -
            log["entry_time"]

        ).total_seconds()


        # ---------------------------------------------
        # BILLING
        # ---------------------------------------------

        # Minimum billing = 15 minutes

        hours = max(

            duration_seconds / 3600,

            0.25
        )


        duration_minutes = round(
            hours * 60
        )


        fee = round(
            duration_minutes /
            60 *
            RATE_PER_HOUR
        )


        # ---------------------------------------------
        # UPDATE LOG
        # ---------------------------------------------

        logs_col.update_one(

            {
                "_id":
                    log["_id"]
            },

            {
                "$set": {

                    "exit_time":
                        exit_time,

                    "fee":
                        fee,

                    "duration_minutes":
                        duration_minutes
                }
            }
        )


        # ---------------------------------------------
        # FREE SLOT
        # ---------------------------------------------

        slots_col.update_one(

            {
                "slot_id":
                    log["slot_id"]
            },

            {
                "$set": {

                    "status":
                        "free",

                    "vehicle_number":
                        None,

                    "vehicle_type":
                        None
                }
            }
        )


        # ---------------------------------------------
        # BILLING RECORD
        # ---------------------------------------------

        billing_id = str(
            uuid4()
        )


        billing_data = {

            "billing_id":
                billing_id,

            "vehicle_number":
                vehicle_number,

            "slot_id":
                log["slot_id"],

            "floor":
                log.get(
                    "floor",
                    "N/A"
                ),

            "entry_time":
                log["entry_time"],

            "exit_time":
                exit_time,

            "duration_hours":
                round(
                    hours,
                    2
                ),

            "rate_per_hour":
                RATE_PER_HOUR,

            "amount":
                fee,

            "billing_time":
                exit_time
        }


        billing_col.insert_one(
            billing_data
        )


        # ---------------------------------------------
        # TRANSACTION
        # ---------------------------------------------

        transaction_data = {

            "transaction_id":
                str(uuid4()),

            "billing_id":
                billing_id,

            "vehicle_number":
                vehicle_number,

            "amount":
                fee,

            "payment_status":
                "paid",

            "payment_method":
                "cash",

            "transaction_time":
                exit_time
        }


        transaction_col.insert_one(
            transaction_data
        )


        return {

            "message":
                "Vehicle exited successfully",

            "vehicle_number":
                vehicle_number,

            "slot_id":
                log["slot_id"],

            "floor":
                log.get(
                    "floor",
                    "N/A"
                ),

            "entry_time":
                str(
                    log.get(
                        "entry_time"
                    )
                ),

            "exit_time":
                str(
                    exit_time
                ),

            "duration_minutes":
                duration_minutes,

            "rate_per_hour":
                RATE_PER_HOUR,

            "fee":
                fee,

            "billing_id":
                billing_id
        }


    except HTTPException:

        raise


    except Exception as e:

        print(
            "EXIT ERROR:",
            str(e)
        )

        raise HTTPException(

            status_code=500,

            detail=str(e)
        )


# =========================================================
# PARKING LOGS
# =========================================================

@app.get("/logs")
def get_logs(

    page: int = 1,

    limit: int = 50,

    vehicle_number: str = None,

    status: str = None
):

    try:

        skip = (
            page - 1
        ) * limit

        query = {}


        # ---------------------------------------------
        # VEHICLE SEARCH
        # ---------------------------------------------

        if vehicle_number:

            query[
                "vehicle_number"
            ] = {

                "$regex":
                    vehicle_number,

                "$options":
                    "i"
            }


        # ---------------------------------------------
        # STATUS FILTER
        # ---------------------------------------------

        if status:

            if status == "occupied":

                query[
                    "exit_time"
                ] = None


            elif status == "exited":

                query[
                    "exit_time"
                ] = {
                    "$ne": None
                }


        # ---------------------------------------------
        # GET DOCUMENTS
        # ---------------------------------------------

        docs = list(

            logs_col.find(
                query,
                {
                    "_id": 0
                }
            )

            .sort(
                "entry_time",
                -1
            )

            .skip(
                skip
            )

            .limit(
                limit
            )
        )


        results = []


        for d in docs:

            results.append({

                "vehicle_number":
                    d.get(
                        "vehicle_number"
                    ),

                "slot_id":
                    d.get(
                        "slot_id"
                    ),

                "floor":
                    d.get(
                        "floor"
                    ),

                "status":

                    "exited"

                    if d.get(
                        "exit_time"
                    )

                    else
                    "occupied",

                "entry_time":

                    d[
                        "entry_time"
                    ].isoformat()

                    if d.get(
                        "entry_time"
                    )

                    else None,

                "exit_time":

                    d[
                        "exit_time"
                    ].isoformat()

                    if d.get(
                        "exit_time"
                    )

                    else None,

                "fee":
                    d.get(
                        "fee",
                        0
                    ),

                "duration":

                    f"{round(d.get('duration_minutes', 0))} mins"

                    if d.get(
                        "duration_minutes"
                    )

                    else "-"
            })


        total = logs_col.count_documents(
            query
        )


        return {

            "logs":
                results,

            "total":
                total,

            "page":
                page,

            "limit":
                limit,

            "total_pages":
                (
                    total +
                    limit -
                    1
                ) // limit
        }


    except Exception as e:

        return {
            "error":
                str(e)
        }