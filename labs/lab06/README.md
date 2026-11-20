# Lab 06 – MongoDB Index Design and Index Strategies

## Overview
This lab explores MongoDB index design, query optimization, index usage statistics, insertion performance, and covered queries.

## Activity 6.1 – Index Design for a Query Workload

### Objective
Design and validate indexes for a realistic query workload.

### Implementation
- Generated 50,000 product documents using Python random data.
- Stored products with name, category, price, rating, stock, and tags.
- Executed five representative queries before creating indexes.
- Used explain() to inspect execution stages and totalDocsExamined.
- Created indexes and repeated the same queries.

### Indexes Created
1. category_price_idx – Compound index on category and price.
2. price_idx – Single-field index on price.
3. tags_idx – Index on tags.
4. name_text_idx – Text index on product name.
5. rating_stock_idx – Compound index on rating and stock.

### Query Results

| Query | Documents Examined Before | After |
|---|---:|---:|
| Category and price sort | 50,000 | 6,248 |
| Price range | 50,000 | 9,907 |
| Tag search | 50,000 | 12,457 |
| Text search | Requires text index | 8,225 |
| Rating and stock sort | 50,000 | 8,427 |

Note: MongoDB requires a text index for the $text query, so it could not execute before index creation.

## Activity 6.1 – Try It Yourself: Index Usage Statistics

### Implementation
- Used the $indexStats aggregation stage.
- Executed the five representative queries five times.
- Collected index access statistics.

### Results

| Index | Operations |
|---|---:|
| price_idx | 5 |
| category_price_idx | 5 |
| name_text_idx | 5 |
| rating_stock_idx | 5 |
| tags_idx | 5 |
| _id_ | 0 |

All five designed indexes were used by the repeated query workload.

## Activity 6.2 – Compare Index Strategies

### Objective
Compare insertion performance and query execution under different index configurations.

### Implementation
1. Inserted 10,000 documents without additional indexes.
2. Created five indexes on different fields.
3. Inserted another 10,000 documents.
4. Measured insertion time using Python's time module.
5. Calculated percentage slowdown.
6. Dropped all indexes except the critical compound index.
7. Repeated the five representative queries.

### Insertion Benchmark

| Configuration | Insertion Time |
|---|---:|
| Without additional indexes | 0.0522 seconds |
| With five indexes | 0.0831 seconds |

Percentage slowdown: 59.19%

### Query Comparison

Documents examined:

| Query | Five Indexes | One Index |
|---|---:|---:|
| Category and price sort | 4,043 | 4,043 |
| Price range | 3,964 | 20,000 |
| Rating filter | 3,948 | 20,000 |
| Stock filter | 16,061 | 20,000 |
| Tag search | 9,929 | 20,000 |

The category_price_idx compound index was retained.

## Activity 6.2 – Try It Yourself: Covered Query

### Objective
Implement a covered query and verify that the FETCH stage is eliminated.

### Implementation
- Created a compound index on category and name.
- Queried category and name fields.
- Excluded _id from the projection.
- Used explain() to inspect the execution plan.

### Results
- Index: category_name_covered_idx
- Execution stages: PROJECTION_COVERED → IXSCAN
- Documents examined: 0
- Keys examined: 4,043
- Documents returned: 4,043
- FETCH stage: Eliminated

The query was successfully covered by the index without fetching documents from the collection.

## Folder Structure

- activity-6.1/ – Index design script and output.
- activity-6.1-try-it-yourself/ – Index usage statistics script and output.
- activity-6.2/ – Index strategy comparison script and output.
- activity-6.2-try-it-yourself/ – Covered query script and output.

## How to Run

Run the following commands from the project root:

    python labs/lab06/activity-6.1/lab_06_1_index_design.py

    python labs/lab06/activity-6.1-try-it-yourself/index_usage_stats.py

    python labs/lab06/activity-6.2/lab_06_2_index_strategies.py

    python labs/lab06/activity-6.2-try-it-yourself/covered_query.py

## Requirements

- Python
- pymongo
- python-dotenv
- MongoDB running locally
- MONGODB_LOCAL_URI configured in the project .env file

## Conclusion

The experiment demonstrated that appropriate indexes reduce the number of documents examined during queries. However, maintaining multiple indexes increases insertion overhead. A covered query can retrieve results directly from an index without fetching documents from the collection.

All four Lab 06 activities were executed successfully. Their terminal outputs are saved as output.txt in the respective activity folders.
