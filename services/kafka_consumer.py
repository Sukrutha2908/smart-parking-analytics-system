import json
import time
from datetime import datetime
import math

from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable

from app.mongodb import (
    slot_collection,
    parking_collection,
    log_collection,
    billing_collection
)


# =========================================================
# WAIT FOR KAFKA
# =========================================================

while True:

    try:

        consumer = KafkaConsumer(
            "parking-events",

            bootstrap_servers="kafka:9092",

            value_deserializer=lambda v:
                json.loads(v.decode("utf-8")),

            auto_offset_reset="earliest",

            enable_auto_commit=True,

            group_id="parking-consumer-group"
        )

        print(
            "Kafka Consumer Connected Successfully"
        )

        break

    except NoBrokersAvailable:

        print(
            "Kafka not ready. "
            "Retrying in 5 seconds..."
        )

        time.sleep(5)


# =========================================================
# PROCESS KAFKA EVENTS
# =========================================================

for message in consumer:

    try:

        event = message.value

        print(
            "Received:",
            event
        )

        slot_id = event.get(
            "slot_id"
        )

        status = event.get(
            "status"
        )

        vehicle_number = event.get(
            "vehicle_number"
        )

        vehicle_type = event.get(
            "vehicle_type"
        )


        if not slot_id or not status:

            print(
                "Invalid event. Skipping..."
            )

            continue


        # =================================================
        # FIND SLOT
        # =================================================

        slot = slot_collection.find_one(
            {
                "slot_id": slot_id
            }
        )


        if not slot:

            print(
                f"Slot {slot_id} not found"
            )

            continue


        floor = slot.get(
            "floor"
        )


        # =================================================
        # VEHICLE ENTERS
        # =================================================

        if status == "occupied":

            entry_time = datetime.utcnow()


            # ---------------------------------------------
            # UPDATE SLOT
            # ---------------------------------------------

            result = slot_collection.update_one(

                {
                    "slot_id": slot_id
                },

                {
                    "$set": {

                        "status":
                            "occupied",

                        "vehicle_number":
                            vehicle_number,

                        "vehicle_type":
                            vehicle_type
                    }
                }
            )


            print(
                f"Updated slot {slot_id} → occupied "
                f"(matched={result.matched_count}, "
                f"modified={result.modified_count})"
            )


            # ---------------------------------------------
            # CHECK EXISTING PARKING RECORD
            # ---------------------------------------------

            existing = parking_collection.find_one(

                {
                    "slot_id":
                        slot_id,

                    "exit_time":
                        None
                }
            )


            if not existing:

                parking_record = {

                    "vehicle_number":
                        vehicle_number,

                    "vehicle_type":
                        vehicle_type,

                    "slot_id":
                        slot_id,

                    "floor":
                        floor,

                    "entry_time":
                        entry_time,

                    "exit_time":
                        None,

                    "duration_minutes":
                        None,

                    "fee":
                        0,

                    "entry_hour":
                        entry_time.hour,

                    "status":
                        "occupied"
                }


                parking_collection.insert_one(
                    parking_record
                )


                print(
                    f"Parking record created for "
                    f"{vehicle_number}"
                )


                # -----------------------------------------
                # CREATE PARKING LOG
                # -----------------------------------------

                log_record = {

                    "vehicle_number":
                        vehicle_number,

                    "slot_id":
                        slot_id,

                    "floor":
                        floor,

                    "vehicle_type":
                        vehicle_type,

                    "entry_time":
                        entry_time,

                    "exit_time":
                        None,

                    "duration_minutes":
                        None,

                    "fee":
                        0,

                    "status":
                        "occupied"
                }


                log_collection.insert_one(
                    log_record
                )


                print(
                    f"Parking log created for "
                    f"{vehicle_number}"
                )


        # =================================================
        # VEHICLE EXITS
        # =================================================

        elif status == "free":

            # ---------------------------------------------
            # FIND ACTIVE PARKING RECORD
            # ---------------------------------------------

            existing = parking_collection.find_one(

                {
                    "slot_id":
                        slot_id,

                    "exit_time":
                        None
                }
            )


            if existing:

                exit_time = datetime.utcnow()

                entry_time = existing.get(
                    "entry_time"
                )


                # -----------------------------------------
                # CALCULATE DURATION
                # -----------------------------------------

                if entry_time:

                    duration_seconds = (
                        exit_time -
                        entry_time
                    ).total_seconds()

                else:

                    duration_seconds = 0


                duration_minutes = max(

                    round(
                        duration_seconds / 60
                    ),

                    1
                )


                # -----------------------------------------
                # CALCULATE FEE
                # ₹20 / HOUR
                # -----------------------------------------

                

                fee = math.ceil(
                    duration_minutes / 60
                ) * 20


                vehicle_number = existing.get(
                    "vehicle_number"
                )

                vehicle_type = existing.get(
                    "vehicle_type"
                )


                # -----------------------------------------
                # UPDATE PARKING
                # -----------------------------------------

                parking_collection.update_one(

                    {
                        "_id":
                            existing["_id"]
                    },

                    {
                        "$set": {

                            "exit_time":
                                exit_time,

                            "duration_minutes":
                                duration_minutes,

                            "fee":
                                fee,

                            "status":
                                "exited"
                        }
                    }
                )


                print(
                    f"Vehicle {vehicle_number} exited. "
                    f"Duration = "
                    f"{duration_minutes} mins, "
                    f"Fee = ₹{fee}"
                )


                # -----------------------------------------
                # UPDATE PARKING LOG
                # -----------------------------------------

                log_result = log_collection.update_one(

                    {
                        "vehicle_number":
                            vehicle_number,

                        "slot_id":
                            slot_id,

                        "status":
                            "occupied"
                    },

                    {
                        "$set": {

                            "exit_time":
                                exit_time,

                            "duration_minutes":
                                duration_minutes,

                            "fee":
                                fee,

                            "status":
                                "exited"
                        }
                    }
                )


                print(
                    f"Parking log updated for "
                    f"{vehicle_number} "
                    f"(matched={log_result.matched_count}, "
                    f"modified={log_result.modified_count})"
                )


                # -----------------------------------------
                # CREATE BILLING RECORD
                # -----------------------------------------

                billing_record = {

                    "vehicle_number":
                        vehicle_number,

                    "slot_id":
                        slot_id,

                    "vehicle_type":
                        vehicle_type,

                    "entry_time":
                        entry_time,

                    "exit_time":
                        exit_time,

                    "duration_minutes":
                        duration_minutes,

                    "amount":
                        fee,

                    "billing_time":
                        exit_time
                }


                billing_collection.insert_one(
                    billing_record
                )


                print(
                    f"Billing record created for "
                    f"{vehicle_number}: ₹{fee}"
                )


            else:

                print(
                    f"No active parking record "
                    f"found for slot {slot_id}"
                )


            # ---------------------------------------------
            # FREE SLOT
            # ---------------------------------------------

            result = slot_collection.update_one(

                {
                    "slot_id":
                        slot_id
                },

                {
                    "$set": {

                        "status":
                            "free",

                        "vehicle_number":
                            None,

                        "vehicle_type":
                            None
                    }
                }
            )


            print(
                f"Updated slot {slot_id} → free "
                f"(matched={result.matched_count}, "
                f"modified={result.modified_count})"
            )


    except Exception as e:

        print(
            "ERROR processing event:",
            str(e)
        )