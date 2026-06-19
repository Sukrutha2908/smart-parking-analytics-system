import time
import random
import json

from kafka import KafkaProducer
from app.mongodb import slot_collection

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

    event = {

        "slot_id": slot["slot_id"],

        "status": new_status
    }

    producer.send(
        "parking-events",
        event
    )

    print("Sent:", event)

    time.sleep(30)