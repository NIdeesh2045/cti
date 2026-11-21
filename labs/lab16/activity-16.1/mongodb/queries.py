
from pymongo import MongoClient
import os

client = MongoClient(
    "localhost",
    27317,
    username="lab13_admin",
    password=os.environ["MONGO_PASSWORD"],
    authSource="admin",
    directConnection=True
)

db = client["university_mongo"]

# 1. Find all courses for a student
def courses_for_student(student_id):
    student = db.students.find_one({"student_id": student_id})
    if not student:
        return []
    return list(db.courses.find(
        {"course_id": {"$in": student["course_ids"]}},
        {"_id": 0}
    ))

# 2. Find all students in a course
def students_in_course(course_id):
    course = db.courses.find_one({"course_id": course_id})
    if not course:
        return []
    return list(db.students.find(
        {"student_id": {"$in": course["student_ids"]}},
        {"_id": 0}
    ))

# 3. Find students who share a course with a student
def shared_course_students(student_id):
    student = db.students.find_one({"student_id": student_id})
    if not student:
        return []

    return list(db.students.find(
        {
            "student_id": {"$ne": student_id},
            "course_ids": {"$in": student["course_ids"]}
        },
        {"_id": 0}
    ))

if __name__ == "__main__":
    print("\n1. Courses for Alice:")
    print(courses_for_student("S001"))

    print("\n2. Students in Database Systems:")
    print(students_in_course("C101"))

    print("\n3. Students sharing courses with Alice:")
    print(shared_course_students("S001"))

    client.close()
