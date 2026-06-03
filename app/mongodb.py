# app/mongodb.py

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_NAME = os.getenv("MONGODB_NAME")

client = AsyncIOMotorClient(MONGODB_URI)

database = client[MONGODB_NAME]

parking_collection = database["parking_data"]