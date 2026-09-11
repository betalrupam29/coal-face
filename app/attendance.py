from datetime import datetime
from zoneinfo import ZoneInfo

from pymongo.errors import DuplicateKeyError

from app.database import attendance_collection
from app.config import TIMEZONE, CAMERA_ID


def mark_attendance(
    worker_id,
    name,
    confidence
):

    now = datetime.now(
        ZoneInfo(TIMEZONE)
    )

    today = now.strftime(
        "%Y-%m-%d"
    )

    attendance = {
        "worker_id": worker_id,
        "name": name,
        "date": today,
        "status": "present",
        "check_in": now,
        "confidence": confidence,
        "camera_id": CAMERA_ID
    }

    try:

        attendance_collection.insert_one(
            attendance
        )

        return {
            "marked": True,
            "status": "success",
            "worker_id": worker_id,
            "name": name,
            "message": "Attendance Done",
            "time": now.isoformat(),
            "confidence": confidence
        }

    except DuplicateKeyError:

        return {
            "marked": False,
            "status": "already_marked",
            "worker_id": worker_id,
            "name": name,
            "message": "Attendance Already Done Today",
            "time": now.isoformat(),
            "confidence": confidence
        }