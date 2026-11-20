# Lab 04 – MongoDB Query Operators, Upserts and Bulk Operations

## Overview

This lab focuses on MongoDB query operators, product inventory management, upsert operations, and bulk write operations using Python and PyMongo.

The practical exercises demonstrate how to filter documents using comparison, logical, and array operators, implement pagination, perform text searches, and manage product records efficiently using upserts and bulk imports.

## Technologies Used

- Python 3
- MongoDB
- PyMongo
- MongoDB Compass
- JSON
- MongoDB Query Operators

---

# Lab 4.1 – Build a Product Query API

## Objective

Implement CRUD-related product inventory queries using different MongoDB query operator categories.

## Implementation

Created a `products` collection in the `lab04_inventory` database with schema validation.

The collection requires:

- `name`: String
- `price`: Positive number
- `stock`: Non-negative integer
- `tags`: Array of strings

Inserted 10 products with different prices, stock quantities, and tags.

## Queries Implemented

### 1. Comparison Operators

- `$gte` and `$lte`: Find products with prices between 20 and 50.
- `$eq`: Find products with stock equal to zero (out of stock).

### 2. Logical Operators

- `$or`: Find products that are either out of stock or priced above 100.
- `$and`: Find products that are in stock and tagged as premium.

### 3. Array Operators

- `$all`: Find products containing both `electronics` and `wireless` tags.
- `$size`: Find products containing exactly two tags.

### 4. Pagination

Implemented a pagination function that accepts a page number and items per page.

Products are sorted alphabetically by name, and the appropriate records are retrieved using:

- `sort()`
- `skip()`
- `limit()`

## Files

- `activity-4.1/products.json`
- `activity-4.1/product_queries.py`
- `activity-4.1/output.txt`

## Activity 4.1 – Try It Yourself

### Objective

Implement text search functionality using MongoDB's `$regex` operator.

### Implementation

Created a product search function that searches product names using:

- `$regex`: Matches a search pattern in product names.
- `$options: "i"`: Performs case-insensitive searching.
- `re.escape()`: Treats the supplied search text as a literal string.

Tested the search using the keyword `wireless`.

### Result

Found two matching products:

1. Wireless Headphones
2. Wireless Mouse

## Files

- `activity-4.1-try-it-yourself/product_search.py`
- `activity-4.1-try-it-yourself/output.txt`

---

# Lab 4.2 – Implement Upsert and Bulk Operations

## Objective

Use MongoDB upserts and bulk write operations for conditional inserts and batch modifications.

## Part 1 – Upsert Operations

Implemented a function using `update_one()` with `upsert=True`.

The function accepts a product SKU and price.

- If the SKU exists, its price is updated.
- If the SKU does not exist, a new product is inserted with default values.

### Result

- Existing product SKU A was updated.
- New product SKU K was inserted.
- Total products after the upsert operations: 11.

## Part 2 – Bulk Write Operations

Implemented five `UpdateOne` operations using `bulk_write()`.

The operations performed were:

- Increase stock by 10 for products A, B, and C using `$inc`.
- Set `is_active` to `false` for products D and E using `$set`.

### Bulk Write Result

| Operation Result | Count |
|---|---:|
| Matched documents | 5 |
| Modified documents | 5 |
| Upserted documents | 0 |

The updated product documents were retrieved to verify the changes.

## Files

- `activity-4.2/upsert_bulk.py`
- `activity-4.2/output.txt`

## Activity 4.2 – Try It Yourself

### Objective

Implement an idempotent bulk import function that avoids duplicate product records when executed multiple times.

### Implementation

Created a bulk import function using:

- `UpdateOne`
- `$set`
- `upsert=True`
- `bulk_write()`

Each product is identified by its SKU.

If a product already exists, its fields are updated. Otherwise, a new document is inserted.

### Results

**First Import**

| Result | Count |
|---|---:|
| Matched | 2 |
| Modified | 1 |
| Upserted | 2 |

**Second Import (Same Data)**

| Result | Count |
|---|---:|
| Matched | 4 |
| Modified | 0 |
| Upserted | 0 |

The second execution did not create duplicate documents.

Total products in the collection: 13.

## Files

- `activity-4.2-try-it-yourself/products_import.json`
- `activity-4.2-try-it-yourself/bulk_import.py`
- `activity-4.2-try-it-yourself/output.txt`

---

# Final Results

All four practical activities were executed successfully.

| Activity | Result |
|---|---|
| Lab 4.1 – Product Query API | Completed |
| Lab 4.1 – Regex Search | Completed |
| Lab 4.2 – Upsert and Bulk Operations | Completed |
| Lab 4.2 – Idempotent Bulk Import | Completed |

## Conclusion

This lab demonstrated how MongoDB query operators can be used to filter and retrieve product information efficiently.

It also demonstrated upsert operations for conditional document insertion and updates, along with bulk writes for processing multiple operations together.

The practical exercises provided experience with comparison, logical, and array operators, pagination, regular expressions, schema validation, and idempotent data imports using PyMongo.