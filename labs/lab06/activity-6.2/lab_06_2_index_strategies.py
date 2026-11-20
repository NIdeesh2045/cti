import os
import random
import time
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING, DESCENDING, TEXT

ROOT_DIR = Path(__file__).resolve().parents[3]
load_dotenv(ROOT_DIR / ".env")

MONGO_URI = os.getenv("MONGODB_LOCAL_URI")

if not MONGO_URI:
    raise ValueError("MONGODB_LOCAL_URI not found in .env")

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
client.admin.command("ping")

db = client["lab06_indexing"]
products = db["index_benchmark"]

products.drop()

random.seed(100)
categories = ["Electronics", "Clothing", "Books", "Home", "Sports"]
tags_pool = ["wireless", "premium", "budget", "sale", "popular", "portable"]

def generate_documents(start, count):
    documents = []

    for i in range(start, start + count):
        documents.append({
            "name": f"Product Model {i}",
            "category": random.choice(categories),
            "price": round(random.uniform(10, 2000), 2),
            "rating": random.choice([1, 2, 3, 4, 5]),
            "stock": random.randint(0, 500),
            "tags": random.sample(tags_pool, 3)
        })

    return documents


def insert_and_measure(start, count, label):
    documents = generate_documents(start, count)

    begin = time.perf_counter()
    products.insert_many(documents)
    elapsed = time.perf_counter() - begin

    print(f"{label}")
    print(f"Inserted documents: {count:,}")
    print(f"Insertion time: {elapsed:.4f} seconds")

    return elapsed


def explain_query(title, query, sort=None):
    cursor = products.find(query)

    if sort:
        cursor = cursor.sort(sort)

    plan = cursor.explain()
    execution = plan.get("executionStats", {})

    print(f"\n{title}")
    print("Documents examined:",
          execution.get("totalDocsExamined", "N/A"))
    print("Keys examined:",
          execution.get("totalKeysExamined", "N/A"))
    print("Documents returned:",
          execution.get("nReturned", "N/A"))


try:
    print("=" * 65)
    print("LAB 6.2 - COMPARE INDEX STRATEGIES")
    print("=" * 65)

    # 1. Insert without additional indexes
    print("\n[1] Insertion benchmark WITHOUT additional indexes")

    time_without = insert_and_measure(
        1, 10000, "Without indexes"
    )

    # 2. Create five indexes
    print("\n[2] Creating five indexes")

    indexes = [
        ([("category", ASCENDING), ("price", ASCENDING)],
         "category_price_idx"),
        ([("price", ASCENDING)], "price_idx"),
        ([("rating", ASCENDING)], "rating_idx"),
        ([("stock", ASCENDING)], "stock_idx"),
        ([("tags", ASCENDING)], "tags_idx")
    ]

    for keys, name in indexes:
        products.create_index(keys, name=name)
        print("Created index:", name)

    # 3. Insert with five indexes
    print("\n[3] Insertion benchmark WITH five indexes")

    time_with = insert_and_measure(
        10001, 10000, "With five indexes"
    )

    # 4. Calculate slowdown
    print("\n[4] Insertion Performance Comparison")

    print(f"Without indexes: {time_without:.4f} seconds")
    print(f"With five indexes: {time_with:.4f} seconds")

    if time_without > 0:
        slowdown = ((time_with - time_without) / time_without) * 100
        print(f"Percentage slowdown: {slowdown:.2f}%")

    # 5. Query performance with five indexes
    print("\n[5] Query performance WITH five indexes")

    explain_query(
        "Q1 - Category and price sort",
        {"category": "Electronics"},
        [("price", ASCENDING)]
    )

    explain_query(
        "Q2 - Price range",
        {"price": {"$gte": 100, "$lte": 500}}
    )

    explain_query(
        "Q3 - Rating filter",
        {"rating": 5}
    )

    explain_query(
        "Q4 - Stock filter",
        {"stock": {"$gte": 100}}
    )

    explain_query(
        "Q5 - Tag search",
        {"tags": "wireless"}
    )

    # 6. Drop all but critical compound index
    print("\n[6] Dropping all but the critical compound index")

    for index_name in [
        "price_idx", "rating_idx", "stock_idx", "tags_idx"
    ]:
        products.drop_index(index_name)
        print("Dropped:", index_name)

    # 7. Query performance with one index
    print("\n[7] Query performance WITH only category_price_idx")

    explain_query(
        "Q1 - Category and price sort",
        {"category": "Electronics"},
        [("price", ASCENDING)]
    )

    explain_query(
        "Q2 - Price range",
        {"price": {"$gte": 100, "$lte": 500}}
    )

    explain_query(
        "Q3 - Rating filter",
        {"rating": 5}
    )

    explain_query(
        "Q4 - Stock filter",
        {"stock": {"$gte": 100}}
    )

    explain_query(
        "Q5 - Tag search",
        {"tags": "wireless"}
    )

    print("\n[8] Final index configuration")

    for name, details in products.index_information().items():
        print(name, ":", details["key"])

    print("\nAnalysis:")
    print(
        "Indexes can improve read queries by reducing document scans. "
        "However, every additional index requires storage and maintenance "
        "during inserts, updates, and deletes. A smaller index set reduces "
        "write overhead but may cause some queries to use collection scans."
    )

    print("\nLab 6.2 completed successfully.")

except Exception as error:
    print("\nERROR:", error)
    raise

finally:
    client.close()
