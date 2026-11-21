
from neo4j import GraphDatabase
import os

URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = os.getenv("NEO4J_PASSWORD", "lab16password")

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))


def courses_for_student(student_id):
    query = """
    MATCH (s:Student {student_id: $student_id})-[:ENROLLED_IN]->(c:Course)
    RETURN c.course_id AS course_id, c.course_name AS course_name
    """
    with driver.session() as session:
        return list(session.run(query, student_id=student_id))


def students_in_course(course_id):
    query = """
    MATCH (s:Student)-[:ENROLLED_IN]->(c:Course {course_id: $course_id})
    RETURN s.student_id AS student_id, s.name AS name
    """
    with driver.session() as session:
        return list(session.run(query, course_id=course_id))


def shared_course_students(student_id):
    query = """
    MATCH (s1:Student {student_id: $student_id})
          -[:ENROLLED_IN]->(c:Course)
          <-[:ENROLLED_IN]-(s2:Student)
    WHERE s2.student_id <> $student_id
    RETURN DISTINCT s2.student_id AS student_id, s2.name AS name
    ORDER BY name
    """
    with driver.session() as session:
        return list(session.run(query, student_id=student_id))


if __name__ == "__main__":
    print("\n1. Courses for Alice:")
    for row in courses_for_student("S001"):
        print(dict(row))

    print("\n2. Students in Database Systems:")
    for row in students_in_course("C101"):
        print(dict(row))

    print("\n3. Students sharing courses with Alice:")
    for row in shared_course_students("S001"):
        print(dict(row))

    driver.close()
