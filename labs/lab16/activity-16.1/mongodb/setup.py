
from pymongo import MongoClient
import os
import sys

# MongoDB connection
MONGO_HOST = "localhost"
MONGO_PORT = 27317
MONGO_USER = "lab13_admin"
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")

if not MONGO_PASSWORD:
    sys.exit("Error: Set MONGO_PASSWORD before running this script.")

client = MongoClient(
    host=MONGO_HOST,
    port=MONGO_PORT,
    username=MONGO_USER,
    password=MONGO_PASSWORD,
    authSource="admin",
    directConnection=True,
    serverSelectionTimeoutMS=5000
)

try:
    client.admin.command("ping")
    print("MongoDB connected successfully.")

    db = client["university_mongo"]

    students = db["students"]
    courses = db["courses"]

    # Clear only the Lab 16 university collections
    students.delete_many({})
    courses.delete_many({})

    # Student documents
    student_data = [
        {
            "student_id": "S001",
            "name": "Alice",
            "department": "CSE",
            "course_ids": ["C101", "C102"]
        },
        {
            "student_id": "S002",
            "name": "Bob",
            "department": "CSE",
            "course_ids": ["C101", "C103"]
        },
        {
            "student_id": "S003",
            "name": "Charlie",
            "department": "AIML",
            "course_ids": ["C102", "C103"]
        },
        {
            "student_id": "S004",
            "name": "David",
            "department": "AIML",
            "course_ids": ["C101", "C102", "C103"]
        }
    ]

    # Course documents
    course_data = [
        {
            "course_id": "C101",
            "course_name": "Database Systems",
            "student_ids": ["S001", "S002", "S004"]
        },
        {
            "course_id": "C102",
            "course_name": "Machine Learning",
            "student_ids": ["S001", "S003", "S004"]
        },
        {
            "course_id": "C103",
            "course_name": "Data Structures",
            "student_ids": ["S002", "S003", "S004"]
        }
    ]

    students.insert_many(student_data)
    courses.insert_many(course_data)

    print("\nUniversity database created successfully!")
    print("Database:", db.name)
    print("Students:", students.count_documents({}))
    print("Courses:", courses.count_documents({}))

except Exception as error:
    print("MongoDB setup failed:", error)
    sys.exit(1)

finally:
    client.close()
