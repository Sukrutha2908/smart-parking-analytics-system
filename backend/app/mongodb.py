from pymongo import MongoClient
from dotenv import load_dotenv
import os


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# READ ENVIRONMENT VARIABLES
# ============================================================

MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME")

if not MONGODB_URL:
    raise RuntimeError("MONGODB_URL is not configured")

if not DATABASE_NAME:
    raise RuntimeError("DATABASE_NAME is not configured")


print(f"DATABASE = {DATABASE_NAME}")


# ============================================================
# MONGODB CLIENT
# ============================================================

client = MongoClient(MONGODB_URL)


# ============================================================
# DATABASE
# ============================================================

db = client[DATABASE_NAME]


# ============================================================
# COLLECTIONS
# ============================================================

parking_collection = db["parking"]

vehicle_collection = db["vehicles"]

slot_collection = db["slots"]

billing_collection = db["billing"]

transaction_collection = db["transactions"]

log_collection = db["parking_logs"]

users_collection = db["users"]


print("MongoDB Connected Successfully")