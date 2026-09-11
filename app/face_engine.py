import face_recognition
import numpy as np

from app.database import workers_collection
from app.config import FACE_DISTANCE_THRESHOLD


known_encodings = []
known_worker_ids = []
known_names = []


def load_known_faces():
    global known_encodings
    global known_worker_ids
    global known_names

    known_encodings = []
    known_worker_ids = []
    known_names = []

    workers = workers_collection.find({
        "active": True
    })

    for worker in workers:

        embedding = worker.get("face_embedding")

        if not embedding:
            continue

        encoding = np.array(
            embedding,
            dtype=np.float64
        )

        known_encodings.append(encoding)

        known_worker_ids.append(
            worker["worker_id"]
        )

        known_names.append(
            worker["name"]
        )

        print(
            f"Loaded worker: "
            f"{worker['worker_id']} - "
            f"{worker['name']}"
        )

    print(
        f"Total faces loaded: {len(known_encodings)}"
    )


def recognize_face(face_encoding):

    if len(known_encodings) == 0:
        return None

    distances = face_recognition.face_distance(
        known_encodings,
        face_encoding
    )

    best_index = int(np.argmin(distances))

    best_distance = float(
        distances[best_index]
    )

    if best_distance <= FACE_DISTANCE_THRESHOLD:

        confidence = max(
            0.0,
            min(
                1.0,
                1.0 - best_distance
            )
        )

        return {
            "worker_id": known_worker_ids[best_index],
            "name": known_names[best_index],
            "distance": best_distance,
            "confidence": confidence
        }

    return None