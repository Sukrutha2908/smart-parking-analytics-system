from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Smart Parking Analytics API Running"}

@app.get("/parking-slots")
def parking_slots():
    return {
        "total_slots": 100,
        "occupied_slots": 65,
        "available_slots": 35
    }

@app.get("/vehicles")
def vehicles():
    return {
        "vehicle_count": 250,
        "active_vehicles": 48
    }
