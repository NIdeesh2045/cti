
import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

URI = os.getenv("MONGODB_LOCAL_URI", "mongodb://localhost:27017")
DB_NAME = "lab03_university"

# Prerequisites are stored as course codes (references).
# This avoids duplicating prerequisite course information.

COURSES = [
    {
        "title": "Python Programming",
        "code": "CS101",
        "instructor": "Dr. Kumar",
        "prerequisites": []
    },
    {
        "title": "Data Structures",
        "code": "CS201",
        "instructor": "Dr. Priya",
        "prerequisites": ["CS101"]
    },
    {
        "title": "Database Management Systems",
        "code": "CS301",
        "instructor": "Dr. Anil",
        "prerequisites": ["CS201"]
    },
    {
        "title": "Machine Learning",
        "code": "CS401",
        "instructor": "Dr. Meera",
        "prerequisites": ["CS201", "CS301"]
    }
]


def main():
    client = MongoClient(URI, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    print("[OK] Connected to MongoDB")

    db = client[DB_NAME]
    collection = db["course_prerequisites"]

    collection.drop()
    collection.insert_many(COURSES)

    print(f"[OK] Inserted {len(COURSES)} courses")

    print("\n=== Course Prerequisites ===")
    for course in collection.find({}, {"_id": 0}):
        print(f"\n{course['code']} - {course['title']}")

        if course["prerequisites"]:
            for code in course["prerequisites"]:
                prerequisite = collection.find_one(
                    {"code": code},
                    {"_id": 0, "title": 1}
                )
                if prerequisite:
                    print(f"  Requires: {code} - {prerequisite['title']}")
        else:
            print("  No prerequisites")

    print("\n=== Design Justification ===")
    print("Prerequisites are stored as references using course codes.")
    print("Multiple courses can share the same prerequisite.")
    print("Changes to a prerequisite course do not require updating")
    print("every course that depends on it.")

    print("\n[OK] Try It Yourself completed")
    client.close()


if __name__ == "__main__":
    main()
