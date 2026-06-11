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

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)