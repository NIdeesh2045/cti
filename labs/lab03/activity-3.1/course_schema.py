
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import CollectionInvalid, OperationFailure

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

MONGODB_URI = os.getenv("MONGODB_LOCAL_URI", "mongodb://localhost:27017")
DB_NAME = "lab03_university"
COLLECTION_NAME = "courses"

COURSE_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["title", "code", "instructor", "schedule"],
        "properties": {
            "title": {"bsonType": "string"},
            "code": {
                "bsonType": "string",
                "pattern": "^[A-Z]{2,4}[0-9]{3}$"
            },
            "instructor": {"bsonType": "string"},
            "schedule": {
                "bsonType": "object",
                "required": ["days", "time", "room"],
                "properties": {
                    "days": {
                        "bsonType": "array",
                        "items": {"bsonType": "string"}
                    },
                    "time": {"bsonType": "string"},
                    "room": {"bsonType": "string"}
                }
            },
            "students": {
                "bsonType": "array",
                "items": {
                    "bsonType": "object",
                    "required": ["name", "id", "grade"],
                    "properties": {
                        "name": {"bsonType": "string"},
                        "id": {"bsonType": "string"},
                        "grade": {"bsonType": "string"}
                    }
                }
            }
        }
    }
}


def main():
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    print("[OK] Connected to MongoDB")

    db = client[DB_NAME]

    if COLLECTION_NAME in db.list_collection_names():
        db.drop_collection(COLLECTION_NAME)

    db.create_collection(
        COLLECTION_NAME,
        validator=COURSE_VALIDATOR,
        validationLevel="strict",
        validationAction="error"
    )

    courses = db[COLLECTION_NAME]

    json_path = Path(__file__).with_name("courses.json")
    with open(json_path, "r", encoding="utf-8") as file:
        course_data = json.load(file)

    result = courses.insert_many(course_data)
    print(f"[OK] Inserted {len(result.inserted_ids)} courses")

    print("\n=== Courses meeting on Monday ===")
    for course in courses.find(
        {"schedule.days": "Monday"},
        {"_id": 0, "title": 1, "code": 1, "schedule": 1}
    ):
        print(f"{course['code']} - {course['title']}")
        print(f"  Time: {course['schedule']['time']}")
        print(f"  Room: {course['schedule']['room']}")

    instructor_name = "Dr. Priya Sharma"
    print(f"\n=== Students taught by {instructor_name} ===")

    pipeline = [
        {"$match": {"instructor": instructor_name}},
        {"$unwind": "$students"},
        {
            "$project": {
                "_id": 0,
                "course": "$title",
                "student_name": "$students.name",
                "student_id": "$students.id",
                "grade": "$students.grade"
            }
        }
    ]

    for student in courses.aggregate(pipeline):
        print(
            f"{student['student_name']} "
            f"({student['student_id']}) - "
            f"{student['course']} - Grade: {student['grade']}"
        )

    print("\n=== Schema validation test ===")
    try:
        courses.insert_one({"title": "Invalid Course"})
        print("[ERROR] Invalid document was accepted")
    except OperationFailure:
        print("[OK] MongoDB rejected the invalid document")

    print("\n[OK] Lab 3.1 completed")
    client.close()


if __name__ == "__main__":
    main()
