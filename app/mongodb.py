from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load .env

load_dotenv()

# Read environment variables

MONGODB_URL = os.getenv("MONGODB_URL")

DATABASE_NAME = os.getenv("DATABASE_NAME")

print("DATABASE =", DATABASE_NAME)

# MongoDB Client

client = MongoClient(MONGODB_URL)

# Database

db = client[DATABASE_NAME]

# Collections

parking_collection = db["parking"]
vehicle_collection = db["vehicles"]
slot_collection = db["slots"]
billing_collection = db["billing"]
transaction_collection = db["transactions"]
log_collection = db["parking_logs"]
print("MongoDB Connected Successfully")
