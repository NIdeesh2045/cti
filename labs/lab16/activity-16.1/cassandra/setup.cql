CREATE KEYSPACE IF NOT EXISTS university
WITH replication = {
    'class': 'SimpleStrategy',
    'replication_factor': 1
};

USE university;

CREATE TABLE IF NOT EXISTS student_courses (
    student_id TEXT,
    student_name TEXT,
    course_id TEXT,
    course_name TEXT,
    PRIMARY KEY (student_id, course_id)
);

CREATE TABLE IF NOT EXISTS course_students (
    course_id TEXT,
    course_name TEXT,
    student_id TEXT,
    student_name TEXT,
    PRIMARY KEY (course_id, student_id)
);

INSERT INTO student_courses (student_id, student_name, course_id, course_name)
VALUES ('S001', 'Alice', 'C101', 'Database Systems');

INSERT INTO student_courses (student_id, student_name, course_id, course_name)
VALUES ('S001', 'Alice', 'C102', 'Machine Learning');

INSERT INTO student_courses (student_id, student_name, course_id, course_name)
VALUES ('S002', 'Bob', 'C101', 'Database Systems');

INSERT INTO student_courses (student_id, student_name, course_id, course_name)
VALUES ('S002', 'Bob', 'C103', 'Data Structures');

INSERT INTO student_courses (student_id, student_name, course_id, course_name)
VALUES ('S003', 'Charlie', 'C102', 'Machine Learning');

INSERT INTO student_courses (student_id, student_name, course_id, course_name)
VALUES ('S003', 'Charlie', 'C103', 'Data Structures');

INSERT INTO student_courses (student_id, student_name, course_id, course_name)
VALUES ('S004', 'David', 'C101', 'Database Systems');

INSERT INTO student_courses (student_id, student_name, course_id, course_name)
VALUES ('S004', 'David', 'C102', 'Machine Learning');

INSERT INTO student_courses (student_id, student_name, course_id, course_name)
VALUES ('S004', 'David', 'C103', 'Data Structures');

INSERT INTO course_students (course_id, course_name, student_id, student_name)
VALUES ('C101', 'Database Systems', 'S001', 'Alice');

INSERT INTO course_students (course_id, course_name, student_id, student_name)
VALUES ('C101', 'Database Systems', 'S002', 'Bob');

INSERT INTO course_students (course_id, course_name, student_id, student_name)
VALUES ('C101', 'Database Systems', 'S004', 'David');

INSERT INTO course_students (course_id, course_name, student_id, student_name)
VALUES ('C102', 'Machine Learning', 'S001', 'Alice');

INSERT INTO course_students (course_id, course_name, student_id, student_name)
VALUES ('C102', 'Machine Learning', 'S003', 'Charlie');

INSERT INTO course_students (course_id, course_name, student_id, student_name)
VALUES ('C102', 'Machine Learning', 'S004', 'David');

INSERT INTO course_students (course_id, course_name, student_id, student_name)
VALUES ('C103', 'Data Structures', 'S002', 'Bob');

INSERT INTO course_students (course_id, course_name, student_id, student_name)
VALUES ('C103', 'Data Structures', 'S003', 'Charlie');

INSERT INTO course_students (course_id, course_name, student_id, student_name)
VALUES ('C103', 'Data Structures', 'S004', 'David');