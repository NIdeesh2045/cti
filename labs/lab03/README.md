# Lab 03 – MongoDB Data Modeling: Embedding and Referencing

## Overview

This lab focuses on MongoDB document modeling techniques, including embedded document schemas, schema validation, referencing, and migration from referenced to embedded designs.

The practical activities demonstrate how to organize related data in MongoDB and compare the advantages and limitations of embedding and referencing.

## Technologies Used

- Python 3
- MongoDB
- PyMongo
- MongoDB Compass
- JSON
- MongoDB Aggregation Pipeline

---

# Lab 3.1 – Design an Embedded Document Schema

## Objective

Design and implement an embedded document schema for a university course enrollment system.

Each course document contains its course details, enrolled students, and schedule information.

## Implementation

Created a `courses` collection in the `lab03_university` database.

Each course document contains:

- **Title:** Course name.
- **Code:** Unique course code.
- **Instructor:** Course instructor's name.
- **Schedule:** Days, time, and classroom.
- **Students:** Embedded student details including name, ID, and grade.

Three course documents were inserted into the collection.

## Schema Validation

MongoDB JSON Schema validation was implemented to enforce the required fields:

- title
- code
- instructor
- schedule

The validator also checks the structure and data types of nested schedule and student information.

An invalid document was intentionally inserted to test validation. MongoDB correctly rejected it.

## Queries Implemented

1. **Monday Schedule:** Retrieved all courses that meet on Monday using the `schedule.days` field.
2. **Students by Instructor:** Used an aggregation pipeline with `$match`, `$unwind`, and `$project` to retrieve students enrolled in courses taught by a specific instructor.

## Files

- `activity-3.1/courses.json`
- `activity-3.1/course_schema.py`
- `activity-3.1/output.txt`

## Activity 3.1 – Try It Yourself

### Objective

Track prerequisite relationships between courses.

### Implementation

Created a separate `course_prerequisites` collection containing four courses.

Prerequisite relationships are stored as course code references rather than embedding complete prerequisite course documents.

### Justification

Referencing was selected because:

- Multiple courses can share the same prerequisite.
- Prerequisite information can be maintained independently.
- Updating a course does not require modifying every course that depends on it.
- It avoids unnecessary duplication of course information.

## Files

- `activity-3.1-try-it-yourself/prerequisites.py`
- `activity-3.1-try-it-yourself/output.txt`

---

# Lab 3.2 – Migrate from Referenced to Embedded Design

## Objective

Convert a referenced document design into an embedded document design and compare their performance characteristics.

## Part 1 – Referenced Design

Created two separate collections in the `lab03_blog` database:

- `posts`
- `comments`

Inserted:
- 5 blog posts.
- 10 comments.

Each comment contains a `post_id` reference linking it to its corresponding post.

## Part 2 – Retrieving Data Using $lookup

Implemented a MongoDB aggregation pipeline using `$lookup` to retrieve a post together with its associated comments.

This allows related information from separate collections to be retrieved in a single aggregation query.

## Part 3 – Embedded Design and Migration

Created a new collection named `posts_embedded`.

Used an aggregation pipeline containing `$lookup`, `$project`, and `$out` to migrate the referenced post and comment data into embedded documents.

Each embedded post now contains its comments as an array.

## Part 4 – Query Comparison

| Design | Method | Queries |
|---|---|---:|
| Referenced | Separate `find()` operations | 2 |
| Referenced | `$lookup` aggregation | 1 |
| Embedded | `find_one()` | 1 |

Embedding provides convenient retrieval when comments are limited and usually accessed together with their post.

Referencing is useful when comments are numerous or need to be managed independently.

## Files

- `activity-3.2/posts.json`
- `activity-3.2/blog_migration.py`
- `activity-3.2/output.txt`

## Activity 3.2 – Try It Yourself

### Objective

Analyze the limitations of embedding when a blog post contains 10,000 comments.

### Implementation

Created a Python simulation containing 10,000 comments in a single post document.

The estimated serialized document size was approximately 1,295.65 KB.

### Why Embedding Becomes Problematic

1. MongoDB has a maximum BSON document size of 16 MB.
2. Large embedded arrays can increase document size significantly.
3. Updating large comment arrays can become expensive.
4. Pagination and independent comment retrieval become harder.
5. Concurrent updates to the same post document can create contention.

### Alternative Design

Use a separate `comments` collection and reference the parent post using `post_id`.

Create an index on `post_id` and retrieve comments in smaller pages using pagination.

This approach is more suitable for posts with a very large number of comments.

## Files

- `activity-3.2-try-it-yourself/large_comments.py`
- `activity-3.2-try-it-yourself/output.txt`

---

# Final Results

All four practical activities were executed successfully.

| Activity | Result |
|---|---|
| Lab 3.1 – Embedded Course Schema | Completed |
| Lab 3.1 – Prerequisite References | Completed |
| Lab 3.2 – Referenced to Embedded Migration | Completed |
| Lab 3.2 – 10,000 Comments Analysis | Completed |

## Conclusion

This lab demonstrated how MongoDB supports both embedded and referenced document models.

Embedding is useful when related data is limited and frequently accessed together. Referencing is more suitable when related data grows significantly, is shared across multiple documents, or needs to be managed independently.

The practical exercises demonstrated schema validation, nested document queries, aggregation pipelines, `$lookup`, and data migration using PyMongo.