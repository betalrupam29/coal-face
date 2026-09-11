import os

from dotenv import load_dotenv

load_dotenv()

TIMEZONE = os.getenv("TIMEZONE", "Asia/Kolkata")

FACE_DISTANCE_THRESHOLD = float(
    os.getenv("FACE_DISTANCE_THRESHOLD", "0.50")
)

CAMERA_ID = os.getenv("CAMERA_ID", "CAM001")