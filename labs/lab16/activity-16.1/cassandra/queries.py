
from cassandra.cluster import Cluster

cluster = Cluster(["127.0.0.1"], port=9042)
session = cluster.connect("university")


# 1. Find all courses for a student
def courses_for_student(student_id):
    query = """
        SELECT course_id, course_name
        FROM student_courses
        WHERE student_id = %s
    """
    return list(session.execute(query, [student_id]))


# 2. Find all students in a course
def students_in_course(course_id):
    query = """
        SELECT student_id, student_name
        FROM course_students
        WHERE course_id = %s
    """
    return list(session.execute(query, [course_id]))


# 3. Find students who share courses with a student
def shared_course_students(student_id):
    courses = courses_for_student(student_id)
    shared_students = set()

    for course in courses:
        students = students_in_course(course.course_id)

        for student in students:
            if student.student_id != student_id:
                shared_students.add(
                    (student.student_id, student.student_name)
                )

    return sorted(shared_students)


if __name__ == "__main__":
    print("\n1. Courses for Alice:")
    for row in courses_for_student("S001"):
        print(row)

    print("\n2. Students in Database Systems:")
    for row in students_in_course("C101"):
        print(row)

    print("\n3. Students sharing courses with Alice:")
    for student in shared_course_students("S001"):
        print(student)

    cluster.shutdown()
