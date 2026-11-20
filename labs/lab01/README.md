# Experiment 1: NoSQL Database Families and Application Mapping

**Course:** 23CSE528 – NoSQL Databases using MongoDB

## 1. Objective

To understand the four major NoSQL database families, classify database products, and identify suitable NoSQL database families for real-world application scenarios.

## 2. Activities Performed

### Activity 1.1 – Classify Database Products

Identified the NoSQL family of five database products and explained their classification, real-world applications, and limitations.

| Product | Family | Best For | Limitation |
|---|---|---|---|
| Amazon S3 | Key-Value / Object Storage | Images, videos, backups and data lakes | No database-style queries on object contents |
| Couchbase | Document | User profiles and product catalogs | Requires careful indexing and memory management |
| Apache HBase | Wide-Column | Large-scale logs and time-series workloads | Complex administration |
| Amazon Neptune | Graph | Fraud detection and social networks | Not ideal for simple key-based lookups |
| Memcached | Key-Value | Session and query caching | In-memory storage without built-in durability |

**Additional classification – ScyllaDB**

ScyllaDB belongs to the Wide-Column family. It is suitable for high-throughput workloads such as IoT data and event storage.

### Activity 1.2 – Map a Real-World Application to NoSQL Families

#### A. Ride-Sharing Application

| Data Domain | NoSQL Family | Recommended Database |
|---|---|---|
| Driver Locations | Key-Value | Redis |
| User Profiles | Document | MongoDB |
| Ride History | Wide-Column / Document | Cassandra / MongoDB |
| Driver-Rider Relationships | Graph | Neo4j |

**Explanation:**

- Driver locations require frequent updates and fast retrieval, making Redis suitable.
- User profiles contain flexible and nested information, making MongoDB suitable.
- Ride history involves frequent writes and date-based queries, making Cassandra or MongoDB suitable.
- Driver-rider relationships require graph traversal, making Neo4j suitable.

#### B. Social Media Analytics Platform

| Data Domain | NoSQL Family | Recommended Database |
|---|---|---|
| Raw Post Storage | Wide-Column | Apache Cassandra |
| Real-Time Analytics | Key-Value | Redis |

**Explanation:**

- Apache Cassandra supports high write throughput and scalable storage for millions of posts.
- Redis provides fast in-memory counters and caching for trending topics and real-time dashboard updates.

## 3. Software Requirements

- Python 3
- Visual Studio Code
- macOS / Windows / Linux

No external Python packages, database server, or Docker container are required for this local implementation.

## 4. Project Files

| File | Description |
|---|---|
| `lab_01_classify_databases.py` | Implements database product classification |
| `lab_02_map_application.py` | Implements real-world application mapping |
| `output.txt` | Contains the captured execution results |
| `README.md` | Experiment documentation |

## 5. Execution Procedure

Run Activity 1.1:

```bash
python3 lab_01_classify_databases.py
```

Run Activity 1.2:

```bash
python3 lab_02_map_application.py
```

To capture both execution results:

```bash
{
    echo "23CSE528 - NOSQL DATABASES USING MONGODB"
    echo "EXPERIMENT 1 - EXECUTION RESULTS"
    python3 lab_01_classify_databases.py &&
    python3 lab_02_map_application.py
} > output.txt 2>&1
```

## 6. Results

Both activities executed successfully.

- Activity 1.1 classified five database products and one additional product.
- Activity 1.2 mapped four ride-sharing data domains and two social media analytics domains.
- Execution results were saved in `output.txt`.

## 7. Conclusion

This experiment demonstrated the four major NoSQL database families: Key-Value, Document, Wide-Column, and Graph.

It also demonstrated that database selection depends on data structure, read/write patterns, scalability, and application requirements. Different components of the same application can use different NoSQL database families according to their individual needs. This approach is known as polyglot persistence.