import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME", "face_attendance")

if not MONGO_URI:
    raise ValueError("MONGO_URI is missing in .env")

client = MongoClient(MONGO_URI)

db = client[DATABASE_NAME]

workers_collection = db["workers"]
attendance_collection = db["attendance"]

workers_collection.create_index(
    [("worker_id", 1)],
    unique=True
)

workers_collection.create_index(
    [("name", 1)],
    unique=True
)

attendance_collection.create_index(
    [("worker_id", 1), ("date", 1)],
    unique=True
)