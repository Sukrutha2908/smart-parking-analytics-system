import time
import random
import json

from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

from app.mongodb import slot_collection


# =========================================================
# VEHICLE TYPES BY FLOOR
# =========================================================

FLOOR_VEHICLE_TYPE = {
    "B1": "Large Vehicle",
    "B2": "Mini Truck",
    "L1": "Four Wheeler",
    "L2": "Two Wheeler",
    "L3": "Two Wheeler"
}


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

        print("Kafka Connected Successfully")

        break

    except NoBrokersAvailable:

        print(
            "Kafka not ready. "
            "Retrying in 30 seconds..."
        )

        time.sleep(30)


# =========================================================
# START SIMULATION
# =========================================================

while True:

    try:

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


        # -------------------------------------------------
        # Select a random slot
        # -------------------------------------------------

        slot = random.choice(slots)

        slot_id = slot.get("slot_id")

        floor = slot.get("floor")

        current_status = slot.get(
            "status",
            "free"
        )


        # =================================================
        # VEHICLE ENTRY
        # =================================================

        if current_status == "free":

            vehicle_number = (
                f"AP39{random.randint(1000, 9999)}"
            )

            vehicle_type = FLOOR_VEHICLE_TYPE.get(
                floor
            )

            if not vehicle_type:

                print(
                    f"Unknown floor {floor}. "
                    "Skipping..."
                )

                time.sleep(30)

                continue


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


        # =================================================
        # VEHICLE EXIT
        # =================================================

        else:

            vehicle_number = slot.get(
                "vehicle_number"
            )

            vehicle_type = slot.get(
                "vehicle_type"
            )


            # -------------------------------------------------
            # Old occupied slots may not have vehicle details
            # -------------------------------------------------

            if not vehicle_number:

                print(
                    f"Slot {slot_id} is occupied "
                    "but has no vehicle number. "
                    "Skipping this cycle."
                )

                time.sleep(30)

                continue


            # -------------------------------------------------
            # Fallback vehicle type for old data
            # -------------------------------------------------

            if not vehicle_type:

                vehicle_type = FLOOR_VEHICLE_TYPE.get(
                    floor,
                    "Unknown"
                )


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


        # =================================================
        # SEND EVENT TO KAFKA
        # =================================================

        producer.send(
            "parking-events",
            event
        )

        producer.flush()


        print(
            "Sent:",
            event
        )


        # =================================================
        # WAIT BEFORE NEXT EVENT
        # =================================================

        time.sleep(30)


    except Exception as e:

        print(
            "SIMULATOR ERROR:",
            str(e)
        )

        time.sleep(30)