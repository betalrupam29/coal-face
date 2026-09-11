import json

import cv2
import numpy as np
import face_recognition

from fastapi import (
    FastAPI,
    WebSocket,
    WebSocketDisconnect
)

from fastapi.middleware.cors import CORSMiddleware

from app.face_engine import (
    load_known_faces,
    recognize_face
)

from app.attendance import (
    mark_attendance
)


app = FastAPI(
    title="Face Attendance API",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.on_event("startup")
def startup():

    print(
        "Loading registered faces..."
    )

    load_known_faces()

    print(
        "Face recognition system ready."
    )


@app.get("/")
def root():

    return {
        "message": "Face Attendance API is running"
    }


@app.get("/health")
def health():

    return {
        "status": "ok"
    }


@app.get("/workers")
def get_workers():

    from app.database import workers_collection

    workers = workers_collection.find(
        {
            "active": True
        },
        {
            "_id": 0,
            "worker_id": 1,
            "name": 1
        }
    )

    return list(workers)


@app.get("/attendance/today")
def get_today_attendance():

    from datetime import datetime
    from zoneinfo import ZoneInfo

    from app.database import attendance_collection

    today = datetime.now(
        ZoneInfo("Asia/Kolkata")
    ).strftime("%Y-%m-%d")

    records = attendance_collection.find(
        {
            "date": today
        },
        {
            "_id": 0
        }
    )

    result = []

    for record in records:

        if "check_in" in record:
            record["check_in"] = record[
                "check_in"
            ].isoformat()

        result.append(record)

    return {
        "date": today,
        "attendance": result
    }


@app.websocket("/ws/attendance")
async def attendance_websocket(
    websocket: WebSocket
):

    await websocket.accept()

    print(
        "Attendance camera connected."
    )

    try:

        while True:

            data = await websocket.receive_bytes()

            if not data:
                continue

            np_array = np.frombuffer(
                data,
                dtype=np.uint8
            )

            frame = cv2.imdecode(
                np_array,
                cv2.IMREAD_COLOR
            )

            if frame is None:

                await websocket.send_text(
                    json.dumps({
                        "type": "error",
                        "message": "Invalid image"
                    })
                )

                continue

            small_frame = cv2.resize(
                frame,
                (0, 0),
                fx=0.25,
                fy=0.25
            )

            rgb_frame = cv2.cvtColor(
                small_frame,
                cv2.COLOR_BGR2RGB
            )

            face_locations = face_recognition.face_locations(
                rgb_frame,
                model="hog"
            )

            face_encodings = face_recognition.face_encodings(
                rgb_frame,
                face_locations
            )

            if not face_encodings:

                await websocket.send_text(
                    json.dumps({
                        "type": "recognition",
                        "status": "not_found",
                        "message": "No Worker Found"
                    })
                )

                continue

            results = []

            for face_encoding in face_encodings:

                worker = recognize_face(
                    face_encoding
                )

                if worker is None:

                    results.append({
                        "status": "not_found",
                        "message": "No Worker Found"
                    })

                    continue

                attendance_result = mark_attendance(
                    worker["worker_id"],
                    worker["name"],
                    worker["confidence"]
                )

                results.append(
                    attendance_result
                )

            await websocket.send_text(
                json.dumps({
                    "type": "recognition",
                    "results": results
                })
            )

    except WebSocketDisconnect:

        print(
            "Attendance camera disconnected."
        )

    except Exception as e:

        print(
            "WebSocket error:",
            e
        )

        try:

            await websocket.send_text(
                json.dumps({
                    "type": "error",
                    "message": str(e)
                })
            )

        except Exception:
            pass