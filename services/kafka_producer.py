import time
import random
import json

from kafka import KafkaProducer

producer = KafkaProducer(

    bootstrap_servers="kafka:9092",

    value_serializer=lambda v:
        json.dumps(v).encode('utf-8')
)

slots = [f"B1-{i}" for i in range(1, 73)]

while True:

    event = {

        "slot_id": random.choice(slots),

        "status": random.choice(
            ["free", "occupied"]
        )
    }

    producer.send(
        "parking-events",
        event
    )

    print("Sent:", event)

    time.sleep(2)