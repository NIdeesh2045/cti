
# Activity 2.2 – Bookstore Price Update Using MongoDB

## Objective
To perform an update operation using PyMongo that increases the price of all books published before 2010 by 10%.

## Technologies Used
- Python 3.13
- MongoDB 7.0 (Docker)
- PyMongo
- MongoDB Compass
- JSON

## Database Details
- Database: `lab02_bookstore`
- Collection: `books`
- Dataset: `books.json`
- Total books inserted: 5

## Implementation

The Python script performs the following operations:

1. Connects to the local MongoDB server running through Docker.
2. Reads book records from `books.json`.
3. Inserts five books into the `books` collection.
4. Displays the book prices before updating.
5. Uses the MongoDB `update_many()` method with the `$mul` operator.
6. Updates only books whose publication year is before 2010.
7. Displays the prices after updating.

### MongoDB Update Query

```python
collection.update_many(
    {"year": {"$lt": 2010}},
    {"$mul": {"price": 1.10}}
)
```

## Execution Results

| Book | Year | Original Price | Updated Price |
|---|---:|---:|---:|
| Clean Code | 2008 | $39.99 | $43.99 |
| Deep Learning | 2016 | $72.00 | $72.00 |
| Designing Data-Intensive Applications | 2017 | $45.99 | $45.99 |
| The Pragmatic Programmer | 2019 | $49.99 | $49.99 |
| Hands-On Machine Learning | 2022 | $59.99 | $59.99 |

- Documents matched: 1
- Documents modified: 1
- Total books: 5

## Verification
The updated document was checked using MongoDB Compass.

Database: `lab02_bookstore`

Collection: `books`

The price of Clean Code, published in 2008, increased from $39.99 to approximately $43.99. Other book prices remained unchanged.

## Conclusion
Successfully implemented and executed a conditional bulk update operation using PyMongo. The `$mul` operator increased the price by 10% only for books published before 2010.

