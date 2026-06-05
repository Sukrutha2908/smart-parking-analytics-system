from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME")

print("Mongo URL:", MONGODB_URL)

client = AsyncIOMotorClient(MONGODB_URL)

db = client[DATABASE_NAME]

parking_collection = db["parking"]

print("MongoDB Atlas Connected")