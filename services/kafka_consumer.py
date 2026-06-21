from kafka import KafkaConsumer
import json
from app.websocket_manager import manager

from app.mongodb import slot_collection

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
                "status": status
            }
        }
    )

    import asyncio
    
    asyncio.run(
        manager.broadcast(data)
    )

    print(
        f"Updated {slot_id} -> {status}"
    )