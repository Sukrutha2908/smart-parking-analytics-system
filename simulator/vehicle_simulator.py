from pymongo import MongoClient

from datetime import datetime
from dotenv import load_dotenv
import random
import time
import os

load_dotenv()

# MongoDB Atlas URI
MONGODB_URI = os.getenv("MONGODB_URI")


try:
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)


    client.admin.command("ping")
    print("MongoDB Atlas Connected Successfully!")

    # ✅ FIXED DATABASE & COLLECTION NAME
    db = client[os.getenv("MONGODB_NAME")]
    parking_slots = db["parking_slots"]

except Exception as e:
    print("MongoDB Connection Failed!")
    print("Error:", e)
    exit()

while True:
    try:
        entry_time = datetime.now()
        duration_minutes = random.randint(15, 300)

        if duration_minutes <= 60:
            fee_category = "Low"
            billing_amount = 20
        elif duration_minutes <= 180:
            fee_category = "Medium"
            billing_amount = 50
        else:
            fee_category = "High"
            billing_amount = 100

        current_hour = entry_time.hour
        peak_hour = "Yes" if (8 <= current_hour <= 11 or 17 <= current_hour <= 21) else "No"

        document = {
            "vehicle_id": f"VID{random.randint(1000,9999)}",
            "vehicle_no": f"AP{random.randint(1000,9999)}",
            "vehicle_type": random.choice(["Bike", "Car", "SUV"]),
            "slot_id": f"SID{random.randint(1,100)}",
            "slot_no": f"SLOT-{random.randint(1,100)}",
            "parking_zone": random.choice(["A", "B", "C"]),
            "status": "Occupied",
            "vehicle_entry_time": entry_time,
            "vehicle_exit_time": None,
            "duration_minutes": duration_minutes,
            "parking_fee_category": fee_category,
            "billing_amount": billing_amount,
            "payment_status": random.choice(["Paid", "Pending"]),
            "payment_method": random.choice(["UPI", "Cash", "Card"]),
            "peak_hour": peak_hour
        }

        result = parking_slots.insert_one(document)

        print("Inserted Successfully! ID:", result.inserted_id)

        time.sleep(5)

    except Exception as e:
        print("Insert Failed!")
        print("Error:", e)
        time.sleep(5)