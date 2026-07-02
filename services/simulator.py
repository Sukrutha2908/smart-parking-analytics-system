import time
import random
import json

from kafka import KafkaProducer
from app.mongodb import slot_collection

import os

KAFKA_SERVER = os.getenv(
    "KAFKA_BOOTSTRAP_SERVERS",
    "localhost:9092"
)

producer = KafkaProducer(

    bootstrap_servers='localhost:9092',

    value_serializer=lambda v:
        json.dumps(v).encode('utf-8')
)

while True:

    slots = list(
        slot_collection.find({})
    )

    slot = random.choice(slots)

    current_status = slot["status"]

    if current_status == "free":

        new_status = "occupied"

    else:

        new_status = "free"

    # Vehicle Type Based on Floor

    if slot["floor"] == "B1":

        vehicle_type = "Truck"

    elif slot["floor"] == "B2":

        vehicle_type = "Truck"

    elif slot["floor"] == "L1":

        vehicle_type = "Car"

    else:

        vehicle_type = "Bike"

    event = {

        "slot_id": slot["slot_id"],

        "status": new_status,

        "vehicle_number":
            f"AP39{random.randint(1000,9999)}",

        "vehicle_type": vehicle_type,

        "entry_time":
            time.time()
    }

    producer.send(
        "parking-events",
        event
    )

    print("Sent:", event)

    time.sleep(30)