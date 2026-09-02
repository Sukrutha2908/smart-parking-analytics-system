import time
import random
import json

from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

from app.mongodb import slot_collection


# =========================================================
# WAIT FOR KAFKA
# =========================================================

while True:

    try:

        producer = KafkaProducer(

            bootstrap_servers="kafka:9092",

            value_serializer=lambda v:
                json.dumps(v).encode("utf-8")
        )

        print(
            "Kafka Connected Successfully"
        )

        break

    except NoBrokersAvailable:

        print(
            "Kafka not ready. "
            "Retrying in 5 seconds..."
        )

        time.sleep(5)


# =========================================================
# START SIMULATION
# =========================================================

while True:

    slots = list(
        slot_collection.find({})
    )


    if not slots:

        print(
            "No parking slots found. "
            "Retrying in 5 seconds..."
        )

        time.sleep(5)

        continue


    # Random slot

    slot = random.choice(
        slots
    )


    slot_id = slot.get(
        "slot_id"
    )

    current_status = slot.get(
        "status",
        "free"
    )


    # =====================================================
    # VEHICLE ENTRY
    # =====================================================

    if current_status == "free":

        vehicle_number = (
            f"AP39{random.randint(1000, 9999)}"
        )


        # Vehicle type based on floor

        if slot.get("floor") == "B1":

            vehicle_type = "Truck"

        elif slot.get("floor") == "B2":

            vehicle_type = "Truck"

        elif slot.get("floor") == "L1":

            vehicle_type = "Car"

        else:

            vehicle_type = "Bike"


        event = {

            "slot_id":
                slot_id,

            "status":
                "occupied",

            "vehicle_number":
                vehicle_number,

            "vehicle_type":
                vehicle_type,

            "entry_time":
                time.time()
        }


        print(
            "Vehicle ENTRY:",
            event
        )


    # =====================================================
    # VEHICLE EXIT
    # =====================================================

    else:

        vehicle_number = slot.get(
            "vehicle_number"
        )

        vehicle_type = slot.get(
            "vehicle_type",
            "Unknown"
        )


        # If old slot data has no vehicle number,
        # don't create an incorrect exit event.

        if not vehicle_number:

            print(
                f"Slot {slot_id} is occupied "
                "but has no vehicle number. "
                "Skipping this cycle."
            )

            time.sleep(30)

            continue


        event = {

            "slot_id":
                slot_id,

            "status":
                "free",

            "vehicle_number":
                vehicle_number,

            "vehicle_type":
                vehicle_type,

            "entry_time":
                time.time()
        }


        print(
            "Vehicle EXIT:",
            event
        )


    # =====================================================
    # SEND TO KAFKA
    # =====================================================

    producer.send(
        "parking-events",
        event
    )

    producer.flush()


    print(
        "Sent:",
        event
    )


    # Wait 30 seconds

    time.sleep(30)