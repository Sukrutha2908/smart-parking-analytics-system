from kafka import KafkaConsumer
import json
from app.websocket_manager import manager

from app.mongodb import slot_collection
from app.mongodb import log_collection
from datetime import datetime
from app.mongodb import billing_collection
from datetime import datetime
from app.mongodb import transaction_collection
import random


import os

KAFKA_SERVER = os.getenv(
    "KAFKA_BOOTSTRAP_SERVERS",
    "localhost:9092"
)

consumer = KafkaConsumer(

    "parking-events",

    bootstrap_servers='localhost:9092',

    value_deserializer=lambda m:
        json.loads(m.decode('utf-8'))
)

print("Kafka Consumer Started...")

for message in consumer:

    data = message.value

    slot_id = data["slot_id"]

    status = data["status"]

    print("Received:", data)

    slot_collection.update_one(

        {"slot_id": slot_id},

        {
            "$set": {

                "status": status,

                "vehicle_number":
                    data.get("vehicle_number"),

                "vehicle_type":
                    data.get("vehicle_type"),

                "entry_time":
                    data.get("entry_time")
            }
        }
    )

    duration = (
        random.randint(10, 180)
        if status == "free"
        else None
    )

    fee = (
        round((duration / 60) * 20)
        if duration
        else None
    )

    log_collection.insert_one({

        "vehicle_number":
            data.get(
                "vehicle_number",
                "SIMULATED"
            ),

        "slot_id":
            data["slot_id"],

        "vehicle_type":
            data.get("vehicle_type"),

        "entry_time":
            datetime.now(),

        "exit_time":
            datetime.now()
            if status == "free"
            else None,

        "status":
            "exited"
            if status == "free"
            else "occupied",

        "duration_minutes":
            duration,

        "fee":
            fee
            
    })


    if status == "free":

        billing_collection.insert_one({
        
            "vehicle_number":
                data.get(
                    "vehicle_number",
                    "SIMULATED"
                ),

            "slot_id":
                data["slot_id"],
            
            "amount":
                random.randint(20, 200),
            
            "billing_time":
                datetime.now()
        })

    transaction_collection.insert_one({
        
        "vehicle_number":
            data.get(           
                "vehicle_number",
                "SIMULATED"
            ),
        
        "slot_id":
            data["slot_id"],
            
        "transaction_type":
            "entry" if data["status"] == "occupied"
            else "exit",
            
        "timestamp":
            datetime.now()
    })

    import asyncio
    
    asyncio.run(
        manager.broadcast(data)
    )

    print(
        f"Updated {slot_id} -> {status}"
    )