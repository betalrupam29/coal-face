import os

import face_recognition

from app.database import workers_collection


FACES_FOLDER = "faces"


def get_next_worker_id():

    workers = list(
        workers_collection.find(
            {},
            {
                "worker_id": 1
            }
        )
    )

    numbers = []

    for worker in workers:

        worker_id = worker.get(
            "worker_id",
            ""
        )

        if worker_id.startswith("W"):

            try:
                number = int(
                    worker_id[1:]
                )

                numbers.append(number)

            except ValueError:
                pass

    if not numbers:
        return "W001"

    return f"W{max(numbers) + 1:03d}"


def register_workers():

    if not os.path.exists(
        FACES_FOLDER
    ):
        print(
            "faces folder not found"
        )
        return

    files = sorted(
        os.listdir(FACES_FOLDER)
    )

    for filename in files:

        if not filename.lower().endswith(
            (".jpg", ".jpeg", ".png")
        ):
            continue

        name = os.path.splitext(
            filename
        )[0]

        path = os.path.join(
            FACES_FOLDER,
            filename
        )

        print(
            f"\nProcessing: {filename}"
        )

        image = face_recognition.load_image_file(
            path
        )

        locations = face_recognition.face_locations(
            image
        )

        if len(locations) == 0:

            print(
                f"No face found: {filename}"
            )

            continue

        if len(locations) > 1:

            print(
                f"Multiple faces found: {filename}"
            )

            continue

        encoding = face_recognition.face_encodings(
            image,
            locations
        )[0]

        existing = workers_collection.find_one(
            {
                "name": name
            }
        )

        if existing:

            workers_collection.update_one(
                {
                    "_id": existing["_id"]
                },
                {
                    "$set": {
                        "face_embedding": encoding.tolist(),
                        "active": True
                    }
                }
            )

            print(
                f"Updated: "
                f"{existing['worker_id']} - {name}"
            )

        else:

            worker_id = get_next_worker_id()

            workers_collection.insert_one(
                {
                    "worker_id": worker_id,
                    "name": name,
                    "face_embedding": encoding.tolist(),
                    "active": True
                }
            )

            print(
                f"Registered: "
                f"{worker_id} - {name}"
            )


if __name__ == "__main__":
    register_workers()