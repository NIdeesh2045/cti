# Lab 05 – MongoDB Aggregation and Lookup

## Overview
This lab demonstrates MongoDB aggregation pipelines, sales analytics, and joins using the `$lookup` operator.

## Activity 5.1 – Sales Analytics Pipeline
- Inserted 24 sales orders into the `orders` collection.
- Calculated monthly revenue using `$group`, `$sum`, `$multiply`, and `$dateToString`.
- Identified the top 3 customers by total spending.
- Calculated average order value for each order status.

## Activity 5.1 – Try It Yourself: Order Value Bucketing
- Used `$addFields` to calculate each order's value.
- Used `$bucket` to categorize orders into Small, Medium, and Large.
- Small: below $50.
- Medium: $50–$200.
- Large: above $200.

## Activity 5.2 – MongoDB Lookup
- Created `products` and `orders` collections with related product IDs.
- Used `$lookup` to join orders with product details.
- Calculated total order value using quantity and product base price.
- Identified products that have never been ordered.

## Activity 5.2 – Try It Yourself: Lookup with Pipeline
- Used `$lookup` with a pipeline.
- Used `let` to pass the current product ID.
- Used `$expr`, `$eq`, and `$gte` to match orders with quantity greater than or equal to 2.

## Folder Structure
- `activity-5.1/` – Sales analytics Python script, JSON data, and output.
- `activity-5.1-try-it-yourself/` – Bucketing Python script, JSON data, and output.
- `activity-5.2/` – Lookup Python script, JSON data, and output.
- `activity-5.2-try-it-yourself/` – Pipeline lookup Python script, JSON data, and output.

## How to Run
Run these commands from the project root:

    python labs/lab05/activity-5.1/sales_analytics.py
    python labs/lab05/activity-5.1-try-it-yourself/bucket_analysis.py
    python labs/lab05/activity-5.2/lookup_joins.py
    python labs/lab05/activity-5.2-try-it-yourself/lookup_pipeline.py

## Requirements
- Python
- pymongo
- python-dotenv
- MongoDB running locally
- MongoDB connection URI configured in the project `.env` file

## Result
All four activities were executed successfully. Their terminal outputs are saved in the respective activity folders as `output.txt`.
